import time
import httpx
from core.config import settings
from core.logger import logger
from data.base import AbstractDataProvider

class GoldAPIProvider(AbstractDataProvider):
    def __init__(self):
        self.api_key = settings.GOLDAPI_KEY
        self.base_url = "https://www.goldapi.io/api"
        self.headers = {"x-access-token": self.api_key, "Content-Type": "application/json"}
        self._cache = {"data": None, "fetched_at": 0.0}

    async def get_latest_price(self, symbol: str = "XAUUSD") -> dict:
        if not self.api_key:
            raise ValueError("GOLDAPI_KEY sozlanmagan")

        now = time.time()
        if self._cache["data"] and (now - self._cache["fetched_at"]) < settings.POLL_INTERVAL_SECONDS:
            return self._cache["data"]

        url = f"{self.base_url}/XAU/USD"
        try:
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            
            price = float(data.get("price", 0.0))
            bid = float(data.get("bid", price - 0.20))
            ask = float(data.get("ask", price + 0.20))
            spread = round(ask - bid, 2)
            open_price = float(data.get("open_price", price))
            high_price = float(data.get("high_price", price))
            low_price = float(data.get("low_price", price))
            ch = float(data.get("ch", 0.0))
            chp = float(data.get("chp", 0.0))
            
            result = {
                "symbol": "XAUUSD",
                "price": price,
                "bid": bid,
                "ask": ask,
                "spread": spread,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "change": ch,
                "change_percent": chp,
                "timestamp": now,
                "source": "GoldAPI.io"
            }
            self._cache["data"] = result
            self._cache["fetched_at"] = now
            return result
        except Exception as e:
            logger.error(f"GoldAPIProvider error: {e}")
            raise

    async def get_historical_candles(self, symbol: str = "XAUUSD", timeframe: str = "15m", limit: int = 100) -> list[dict]:
        # GoldAPI free plan does not provide historical candles endpoint reliably
        # Handled by Yahoo Finance fallback or calculated from ticks
        return []
