from abc import ABC, abstractmethod
from typing import Any

class AbstractDataProvider(ABC):
    @abstractmethod
    async def get_latest_price(self, symbol: str = "XAUUSD") -> dict[str, Any]:
        """
        Must return dict with keys:
        'symbol', 'price', 'bid', 'ask', 'spread', 'open', 'high', 'low', 'change', 'change_percent', 'timestamp', 'source'
        """
        pass

    @abstractmethod
    async def get_historical_candles(self, symbol: str = "XAUUSD", timeframe: str = "15m", limit: int = 100) -> list[dict[str, Any]]:
        """
        Must return list of dicts with keys:
        'symbol', 'timeframe', 'timestamp', 'open', 'high', 'low', 'close', 'volume'
        """
        pass
