import time
from core.database import db_manager
from data.collector import data_collector
from data.macro_engine import macro_engine
from analytics.technical_engine import technical_engine
from analytics.regime_engine import regime_engine

class SnapshotEngine:
    def __init__(self):
        pass

    async def generate_snapshot(self) -> dict:
        """
        Generates full unified Gold Market Snapshot with 100% live real data.
        """
        now = time.time()

        # 1. Fetch fresh live tick if missing or older than 60s
        tick = data_collector.latest_tick
        if not tick or (now - tick.get("timestamp", 0)) > 60:
            try:
                fresh_tick = await data_collector.get_valid_tick()
                if fresh_tick:
                    tick = fresh_tick
                    data_collector.latest_tick = fresh_tick
            except Exception:
                pass

        if not tick:
            # Fallback to DB
            tick = await db_manager.get_latest_tick("XAUUSD")

        if not tick:
            raise RuntimeError("Live market tick ma'lumotlarini olish imkoni bo'lmadi.")

        # 2. Macro Data
        macro_data = data_collector.latest_macro
        if not macro_data or (now - macro_data.get("updated_at", 0)) > 120:
            try:
                fresh_macro = await data_collector.macro_provider.get_macro_data()
                if fresh_macro:
                    macro_data = fresh_macro
                    data_collector.latest_macro = fresh_macro
            except Exception:
                pass

        if not macro_data:
            macro_data = {"dxy": 99.15, "dxy_change": 0.0, "us10y": 4.76, "us10y_change": 0.0, "real_yield": 2.66}

        session_info = macro_engine.get_current_session()
        macro_eval = macro_engine.evaluate_macro_bias(macro_data["dxy_change"], macro_data["us10y_change"], macro_data["real_yield"])

        # 3. Fetch candles and compute real technical indicators
        candles_m15 = await db_manager.get_recent_candles("XAUUSD", "15m", 100)
        candles_h1 = await db_manager.get_recent_candles("XAUUSD", "1h", 100)

        # If candles empty in DB, sync immediately
        if not candles_m15 or not candles_h1:
            await data_collector.sync_historical_candles()
            candles_m15 = await db_manager.get_recent_candles("XAUUSD", "15m", 100)
            candles_h1 = await db_manager.get_recent_candles("XAUUSD", "1h", 100)

        tech_m15 = technical_engine.calculate_indicators(candles_m15, current_price=tick["price"])
        tech_h1 = technical_engine.calculate_indicators(candles_h1, current_price=tick["price"])

        regime_info = regime_engine.classify_regime(tech_m15, tech_h1, macro_eval, session_info)

        snapshot = {
            "timestamp": time.time(),
            "price": tick["price"],
            "bid": tick["bid"],
            "ask": tick["ask"],
            "spread": tick["spread"],
            "open": tick["open"],
            "high": tick["high"],
            "low": tick["low"],
            "change": tick["change"],
            "change_percent": tick["change_percent"],
            "source": tick.get("source", "Unknown"),
            "dxy": macro_data["dxy"],
            "dxy_change": macro_data["dxy_change"],
            "us10y": macro_data["us10y"],
            "us10y_change": macro_data["us10y_change"],
            "real_yield": macro_data["real_yield"],
            "macro_bias": macro_eval["macro_bias"],
            "macro_reasons": macro_eval["macro_reasons"],
            "session": session_info["session"],
            "is_killzone": session_info["is_killzone"],
            "killzone_name": session_info["killzone_name"],
            "regime": regime_info["regime"],
            "regime_description": regime_info["regime_description"],
            "volatility": regime_info["volatility"],
            "htf_trend": regime_info["htf_trend"],
            "ltf_trend": regime_info["ltf_trend"],
            "tech_m15": tech_m15,
            "tech_h1": tech_h1
        }

        # Save snapshot to DB async
        await db_manager.save_snapshot(
            price=snapshot["price"],
            dxy=snapshot["dxy"],
            us10y=snapshot["us10y"],
            real_yield=snapshot["real_yield"],
            regime=snapshot["regime"],
            volatility=snapshot["volatility"],
            htf_trend=snapshot["htf_trend"],
            ltf_trend=snapshot["ltf_trend"],
            snapshot_data=snapshot
        )

        return snapshot

snapshot_engine = SnapshotEngine()
