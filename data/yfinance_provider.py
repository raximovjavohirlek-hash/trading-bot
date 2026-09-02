import time
import httpx
from core.logger import logger
from data.base import AbstractDataProvider

class YahooFinanceProvider(AbstractDataProvider):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache'
        }
        self.symbol_map = {
            "XAUUSD": "GC=F",
            "DXY": "DX-Y.NYB",
            "US10Y": "^TNX"
        }

    async def get_latest_price(self, symbol: str = "XAUUSD") -> dict:
        yf_symbol = self.symbol_map.get(symbol, symbol)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_symbol}?interval=1m&range=1d"
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=10) as client:
                resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            meta = data['chart']['result'][0]['meta']
            
            price = float(meta.get('regularMarketPrice', 0.0))
            prev_close = float(meta.get('chartPreviousClose', price))
            ch = round(price - prev_close, 2)
            chp = round((ch / prev_close) * 100, 2) if prev_close else 0.0
            
            # Estimate Bid/Ask from regular market price
            bid = round(price - 0.15, 2)
            ask = round(price + 0.15, 2)
            spread = round(ask - bid, 2)
            
            high = float(meta.get('regularMarketDayHigh', price))
            low = float(meta.get('regularMarketDayLow', price))
            
            return {
                "symbol": symbol,
                "price": price,
                "bid": bid,
                "ask": ask,
                "spread": spread,
                "open": prev_close,
                "high": high,
                "low": low,
                "change": ch,
                "change_percent": chp,
                "timestamp": time.time(),
                "source": "YahooFinance (GC=F)"
            }
        except Exception as e:
            logger.error(f"YahooFinanceProvider error ({symbol}): {e}")
            raise

    async def get_macro_data(self) -> dict:
        """Fetches DXY and US10Y in parallel."""
        dxy_data = {"price": 104.20, "change": 0.0}
        us10y_data = {"price": 4.25, "change": 0.0}
        
        try:
            dxy_res = await self.get_latest_price("DXY")
            dxy_data = {"price": dxy_res["price"], "change": dxy_res["change"]}
        except Exception as e:
            logger.warning(f"DXY olib bo'lmadi, default ishlatilmoqda: {e}")
            
        try:
            us10y_res = await self.get_latest_price("US10Y")
            us10y_data = {"price": us10y_res["price"], "change": us10y_res["change"]}
        except Exception as e:
            logger.warning(f"US10Y olib bo'lmadi, default ishlatilmoqda: {e}")

        # Real Yield approximation: US10Y - Inflation Expectation (~2.1%)
        real_yield = round(us10y_data["price"] - 2.10, 3)

        return {
            "dxy": dxy_data["price"],
            "dxy_change": dxy_data["change"],
            "us10y": us10y_data["price"],
            "us10y_change": us10y_data["change"],
            "real_yield": real_yield
        }

    async def get_historical_candles(self, symbol: str = "XAUUSD", timeframe: str = "15m", limit: int = 100) -> list[dict]:
        yf_symbol = self.symbol_map.get(symbol, symbol)
        
        # Map timeframe to yfinance interval and range
        interval_map = {
            "1m": ("1m", "1d"),
            "5m": ("5m", "5d"),
            "15m": ("15m", "5d"),
            "1h": ("60m", "1mo"),
            "4h": ("60m", "3mo"),
            "1d": ("1d", "1y")
        }
        interval, range_param = interval_map.get(timeframe, ("15m", "5d"))
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_symbol}?interval={interval}&range={range_param}"
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=10) as client:
                resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            result_node = data['chart']['result'][0]
            timestamps = result_node['timestamp']
            quote = result_node['indicators']['quote'][0]
            
            opens = quote.get('open', [])
            highs = quote.get('high', [])
            lows = quote.get('low', [])
            closes = quote.get('close', [])
            volumes = quote.get('volume', [])
            
            candles = []
            for i in range(len(timestamps)):
                if opens[i] is not None and closes[i] is not None:
                    candles.append({
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "timestamp": float(timestamps[i]),
                        "open": float(opens[i]),
                        "high": float(highs[i]),
                        "low": float(lows[i]),
                        "close": float(closes[i]),
                        "volume": float(volumes[i] or 0)
                    })
            
            return candles[-limit:]
        except Exception as e:
            logger.error(f"YahooFinance candles error ({symbol}, {timeframe}): {e}")
            return []
