import time
import httpx
from core.logger import logger
from data.base import AbstractDataProvider

class BinanceGoldProvider(AbstractDataProvider):
    """
    Fetches 100% REAL live market spot gold data from Binance (PAXG/USDT).
    PAXG is Paxos Gold, physically backed 1:1 by fine troy ounce gold bars.
    Requires no API key and provides real bid, ask, volume, and OHLCV candles.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

    async def get_latest_price(self, symbol: str = "XAUUSD") -> dict:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT"
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=8) as client:
                resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

            price = float(data.get("lastPrice", 0.0))
            bid = float(data.get("bidPrice", price))
            ask = float(data.get("askPrice", price))
            spread = round(ask - bid, 2)
            open_p = float(data.get("openPrice", price))
            high_p = float(data.get("highPrice", price))
            low_p = float(data.get("lowPrice", price))
            ch = round(float(data.get("priceChange", 0.0)), 2)
            chp = round(float(data.get("priceChangePercent", 0.0)), 2)

            return {
                "symbol": "XAUUSD",
                "price": price,
                "bid": bid,
                "ask": ask,
                "spread": spread,
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "change": ch,
                "change_percent": chp,
                "timestamp": time.time(),
                "source": "Binance Live (PAXG/USDT)"
            }
        except Exception as e:
            logger.error(f"BinanceGoldProvider price error: {e}")
            raise

    async def get_historical_candles(self, symbol: str = "XAUUSD", timeframe: str = "15m", limit: int = 100) -> list[dict]:
        interval_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"
        }
        interval = interval_map.get(timeframe, "15m")
        url = f"https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval={interval}&limit={limit}"
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=8) as client:
                resp = await client.get(url)
            resp.raise_for_status()
            raw_klines = resp.json()

            candles = []
            for item in raw_klines:
                candles.append({
                    "symbol": "XAUUSD",
                    "timeframe": timeframe,
                    "timestamp": float(item[0]) / 1000.0,
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5])
                })
            return candles
        except Exception as e:
            logger.error(f"BinanceGoldProvider candles error ({timeframe}): {e}")
            return []
