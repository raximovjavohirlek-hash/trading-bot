from __future__ import annotations
import asyncio
import time
from typing import Optional, Dict, Any
from core.config import settings
from core.logger import logger
from core.database import db_manager
from data.tradingview_provider import TradingViewGoldProvider
from data.binance_provider import BinanceGoldProvider
from data.goldapi_provider import GoldAPIProvider
from data.yfinance_provider import YahooFinanceProvider
from data.data_quality import data_quality_engine

class MarketDataCollector:
    def __init__(self):
        self.tradingview = TradingViewGoldProvider()
        self.binance = BinanceGoldProvider()
        self.goldapi = GoldAPIProvider()
        self.yfinance = YahooFinanceProvider()
        self.is_running = False
        self.latest_tick: Optional[Dict[str, Any]] = None
        self.latest_macro: Optional[Dict[str, Any]] = None
        self.active_provider_name = "TradingView (OANDA)"

    async def start(self):
        self.is_running = True
        logger.info("MarketDataCollector background servisi ishga tushdi.")
        
        # Initial candle sync
        asyncio.create_task(self.sync_historical_candles())

        while self.is_running:
            try:
                tick = await self.get_valid_tick()
                if tick:
                    self.latest_tick = tick
                    # Save to DB
                    await db_manager.save_tick(
                        symbol=tick["symbol"],
                        bid=tick["bid"],
                        ask=tick["ask"],
                        last=tick["price"],
                        spread=tick["spread"],
                        source=tick["source"]
                    )
                
                # Periodically update macro data (every 120s)
                if not self.latest_macro or (time.time() - self.latest_macro.get("updated_at", 0)) > 120:
                    macro = await self.yfinance.get_macro_data()
                    macro["updated_at"] = time.time()
                    self.latest_macro = macro

            except Exception as e:
                logger.error(f"DataCollector siklida xatolik: {e}")

            await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)

    async def get_valid_tick(self) -> Optional[Dict[str, Any]]:
        # 1. Primary: TradingView (OANDA Live Institutional Spot Gold)
        try:
            tick = await self.tradingview.get_latest_price("XAUUSD")
            is_valid, reason = data_quality_engine.validate_tick(tick)
            if is_valid:
                self.active_provider_name = "TradingView (OANDA)"
                return tick
        except Exception as e:
            logger.warning(f"TradingView provider error: {e}")

        # 2. Secondary: Binance Live Market (PAXG/USDT 100% Real Physical Gold)
        try:
            tick = await self.binance.get_latest_price("XAUUSD")
            is_valid, reason = data_quality_engine.validate_tick(tick)
            if is_valid:
                self.active_provider_name = "Binance Live (PAXG/USDT)"
                return tick
        except Exception:
            pass

        # 3. GoldAPI if key configured
        if settings.GOLDAPI_KEY and settings.GOLDAPI_KEY != "your_goldapi_key_here":
            try:
                tick = await self.goldapi.get_latest_price("XAUUSD")
                is_valid, reason = data_quality_engine.validate_tick(tick)
                if is_valid:
                    self.active_provider_name = "GoldAPI.io"
                    return tick
            except Exception:
                pass

        # 4. Fallback: YahooFinance (GC=F)
        try:
            tick = await self.yfinance.get_latest_price("XAUUSD")
            is_valid, reason = data_quality_engine.validate_tick(tick)
            if is_valid:
                self.active_provider_name = tick.get("source", "YahooFinance")
                return tick
        except Exception:
            pass

        # 5. Fallback: SQLite DB Cache
        db_tick = await db_manager.get_latest_tick("XAUUSD")
        if db_tick:
            self.active_provider_name = "SQLite DB Cache"
            return db_tick

        return None

    async def sync_historical_candles(self):
        """Fetches multi-timeframe candles (15m, 1h, 4h, 1d) from Binance / YahooFinance."""
        logger.info("Tarixiy shamlarni ma'lumotlar bazasiga sinxronlash boshlandi...")
        timeframes = ["15m", "1h", "4h", "1d"]
        for tf in timeframes:
            candles = []
            try:
                candles = await self.binance.get_historical_candles("XAUUSD", timeframe=tf, limit=150)
            except Exception:
                pass

            if not candles:
                try:
                    candles = await self.yfinance.get_historical_candles("XAUUSD", timeframe=tf, limit=150)
                except Exception:
                    pass

            if candles:
                await db_manager.save_candles(candles)
                logger.info(f"Sinxronlandi: {tf} ramkasi uchun {len(candles)} ta real sham.")
            await asyncio.sleep(0.5)

    def stop(self):
        self.is_running = False
        logger.info("MarketDataCollector to'xtatildi.")

data_collector = MarketDataCollector()
