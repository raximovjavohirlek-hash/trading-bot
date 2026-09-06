from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import aiosqlite
from core.config import settings
from core.logger import logger

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = str(db_path or settings.DB_PATH)

    async def init_db(self):
        """Creates necessary tables and indexes if they do not exist."""
        logger.info(f"DB initialize qilinmoqda: {self.db_path}")
        async with aiosqlite.connect(self.db_path) as db:
            # Ticks Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ticks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    symbol TEXT NOT NULL,
                    bid REAL NOT NULL,
                    ask REAL NOT NULL,
                    last REAL NOT NULL,
                    spread REAL NOT NULL,
                    volume REAL DEFAULT 0,
                    source TEXT NOT NULL
                )
            """)
            
            # Candles Table (OHLCV)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS candles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL DEFAULT 0,
                    UNIQUE(symbol, timeframe, timestamp)
                )
            """)
            
            # Market Snapshots Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS market_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    price REAL NOT NULL,
                    dxy REAL,
                    us10y REAL,
                    real_yield REAL,
                    regime TEXT NOT NULL,
                    volatility TEXT NOT NULL,
                    htf_trend TEXT NOT NULL,
                    ltf_trend TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL
                )
            """)

            # AI Analyses Log Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ai_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    bias TEXT NOT NULL,
                    confidence INTEGER NOT NULL,
                    reasons_json TEXT NOT NULL,
                    counter_evidence_json TEXT NOT NULL,
                    invalidation_price REAL,
                    status TEXT NOT NULL,
                    raw_response TEXT
                )
            """)

            # Paper Trades Table (Research Mode)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS paper_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    symbol TEXT NOT NULL,
                    type TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    sl REAL NOT NULL,
                    tp REAL NOT NULL,
                    status TEXT NOT NULL,
                    pnl REAL DEFAULT 0.0,
                    close_timestamp REAL
                )
            """)

            # System Alerts Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    level TEXT NOT NULL
                )
            """)

            # Subscribers Table (For automated high-confidence alerts)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    chat_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at REAL
                )
            """)

            await db.commit()
        logger.info("Ma'lumotlar bazasi tayyorlandi.")

    async def save_tick(self, symbol: str, bid: float, ask: float, last: float, spread: float, source: str, volume: float = 0):
        now = datetime.now(timezone.utc).timestamp()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO ticks (timestamp, symbol, bid, ask, last, spread, volume, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (now, symbol, bid, ask, last, spread, volume, source)
            )
            await db.commit()

    async def get_latest_tick(self, symbol: str = "XAUUSD") -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM ticks WHERE symbol = ? ORDER BY id DESC LIMIT 1", (symbol,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def save_candles(self, candles_data: List[Dict[str, Any]]):
        if not candles_data:
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany(
                """INSERT OR REPLACE INTO candles (symbol, timeframe, timestamp, open, high, low, close, volume)
                VALUES (:symbol, :timeframe, :timestamp, :open, :high, :low, :close, :volume)""",
                candles_data
            )
            await db.commit()

    async def get_recent_candles(self, symbol: str = "XAUUSD", timeframe: str = "15m", limit: int = 100) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT * FROM candles WHERE symbol = ? AND timeframe = ? ORDER BY timestamp DESC LIMIT ?""",
                (symbol, timeframe, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                result = [dict(r) for r in rows]
                result.reverse()
                return result

    async def save_snapshot(self, price: float, dxy: float, us10y: float, real_yield: float, regime: str, volatility: str, htf_trend: str, ltf_trend: str, snapshot_data: dict):
        now = datetime.now(timezone.utc).timestamp()
        snapshot_json = json.dumps(snapshot_data, ensure_ascii=False)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO market_snapshots 
                (timestamp, price, dxy, us10y, real_yield, regime, volatility, htf_trend, ltf_trend, snapshot_json) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (now, price, dxy, us10y, real_yield, regime, volatility, htf_trend, ltf_trend, snapshot_json)
            )
            await db.commit()

    async def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM market_snapshots ORDER BY id DESC LIMIT 1"
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    res = dict(row)
                    res['snapshot_data'] = json.loads(res['snapshot_json'])
                    return res
                return None

    async def save_ai_analysis(self, bias: str, confidence: int, reasons: list, counter_evidence: list, invalidation_price: float, status: str, raw_response: str):
        now = datetime.now(timezone.utc).timestamp()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO ai_analyses 
                (timestamp, bias, confidence, reasons_json, counter_evidence_json, invalidation_price, status, raw_response) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (now, bias, confidence, json.dumps(reasons), json.dumps(counter_evidence), invalidation_price, status, raw_response)
            )
            await db.commit()

    async def get_latest_ai_analysis(self) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM ai_analyses ORDER BY id DESC LIMIT 1"
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    res = dict(row)
                    res['reasons'] = json.loads(res['reasons_json'])
                    res['counter_evidence'] = json.loads(res['counter_evidence_json'])
                    return res
                return None

    async def save_paper_trade(self, symbol: str, trade_type: str, entry_price: float, sl: float, tp: float) -> int:
        now = datetime.now(timezone.utc).timestamp()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO paper_trades (timestamp, symbol, type, entry_price, sl, tp, status, pnl)
                VALUES (?, ?, ?, ?, ?, ?, 'OPEN', 0.0)""",
                (now, symbol, trade_type, entry_price, sl, tp)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_open_paper_trades(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM paper_trades WHERE status = 'OPEN' ORDER BY id DESC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def update_paper_trade(self, trade_id: int, status: str, pnl: float):
        now = datetime.now(timezone.utc).timestamp()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE paper_trades SET status = ?, pnl = ?, close_timestamp = ? WHERE id = ?",
                (status, pnl, now, trade_id)
            )
            await db.commit()

    async def save_alert(self, alert_type: str, message: str, level: str = "INFO"):
        now = datetime.now(timezone.utc).timestamp()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO system_alerts (timestamp, alert_type, message, level) VALUES (?, ?, ?, ?)",
                (now, alert_type, message, level)
            )
            await db.commit()

    async def add_subscriber(self, chat_id: int, username: str = None, first_name: str = None):
        now = datetime.now(timezone.utc).timestamp()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO subscribers (chat_id, username, first_name, created_at)
                VALUES (?, ?, ?, ?)""",
                (chat_id, username or "", first_name or "", now)
            )
            await db.commit()

    async def get_subscribers(self) -> List[int]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT chat_id FROM subscribers") as cursor:
                rows = await cursor.fetchall()
                return [r[0] for r in rows]

db_manager = DatabaseManager()
