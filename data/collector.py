from __future__ import annotations
import asyncio
import time
from typing import Optional, Dict, Any
from core.config import settings
from core.logger import logger
from core.database import db_manager
from data.goldapi_provider import GoldAPIProvider
from data.yfinance_provider import YahooFinanceProvider
from data.data_quality import data_quality_engine

class MarketDataCollector:
    def __init__(self):
        self.goldapi = GoldAPIProvider()
        self.yfinance = YahooFinanceProvider()
        self.is_running = False
        self.latest_tick: Optional[Dict[str, Any]] = None
        self.latest_macro: Optional[Dict[str, Any]] = None
        self.active_provider_name = "GoldAPI"

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
                
                # Periodically update macro data (every 30s)
                if not self.latest_macro or (time.time() - self.latest_macro.get("updated_at", 0)) > 30:
                    macro = await self.yfinance.get_macro_data()
                    macro["updated_at"] = time.time()
                    self.latest_macro = macro

            except Exception as e:
                logger.error(f"DataCollector siklida xatolik: {e}")

            await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)

    async def get_valid_tick(self) -> Optional[Dict[str, Any]]:
        # 1. Try GoldAPI if key exists
        if settings.GOLDAPI_KEY:
            try:
                tick = await self.goldapi.get_latest_price("XAUUSD")
                is_valid, reason = data_quality_engine.validate_tick(tick)
                if is_valid:
                    self.active_provider_name = "GoldAPI.io"
                    return tick
                else:
                    logger.warning(f"GoldAPI ma'lumoti rad etildi ({reason}), YahooFinance provayderiga o'tilmoqda...")
            except Exception as exc:
                logger.warning(f"GoldAPI ishlamadi ({exc}), YahooFinance provayderiga o'tilmoqda...")

        # 2. Fallback to YahooFinance (GC=F)
        try:
            tick = await self.yfinance.get_latest_price("XAUUSD")
            is_valid, reason = data_quality_engine.validate_tick(tick)
            if is_valid:
                self.active_provider_name = "YahooFinance (GC=F)"
                return tick
            else:
                logger.error(f"YahooFinance ma'lumoti ham rad etildi: {reason}")
        except Exception as exc:
            logger.error(f"YahooFinance ham ishlamadi: {exc}")

        return None

    async def sync_historical_candles(self):
        """Fetches and saves multi-timeframe candles (15m, 1h, 4h, 1d) into SQLite."""
        logger.info("Tarixiy shamlarni ma'lumotlar bazasiga sinxronlash boshlandi...")
        timeframes = ["15m", "1h", "4h", "1d"]
        for tf in timeframes:
            try:
                candles = await self.yfinance.get_historical_candles("XAUUSD", timeframe=tf, limit=150)
                if candles:
                    await db_manager.save_candles(candles)
                    logger.info(f"Sinxronlandi: {tf} ramkasi uchun {len(candles)} ta sham.")
            except Exception as e:
                logger.error(f"Sham sinxronlashda xatolik ({tf}): {e}")

    def stop(self):
        self.is_running = False
        logger.info("MarketDataCollector to'xtatildi.")

data_collector = MarketDataCollector()
