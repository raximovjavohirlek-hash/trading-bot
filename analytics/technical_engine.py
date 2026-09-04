import numpy as np
import pandas as pd
from core.logger import logger

class TechnicalEngine:
    def __init__(self):
        pass

    @staticmethod
    def calculate_indicators(candles: list[dict], current_price: float = None) -> dict:
        """
        Calculates EMA20, EMA50, EMA200, RSI14, ATR14, S/R Levels, SMC & CRT indicators.
        Expects candles sorted from oldest to newest.
        """
        if not candles or len(candles) < 20:
            return {
                "trend": "NEUTRAL",
                "rsi": 50.0,
                "atr": 5.0,
                "ema20": 0.0,
                "ema50": 0.0,
                "ema200": 0.0,
                "support_levels": [],
                "resistance_levels": [],
                "smc": {"structure": "NEUTRAL", "fvg_detected": False, "fvg_type": "NONE", "order_block": None},
                "crt": {"asian_high": 0.0, "asian_low": 0.0, "swept": "NONE"}
            }

        df = pd.DataFrame(candles)
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)

        # 1. Moving Averages
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema200'] = df['close'].ewm(span=200, adjust=False).mean() if len(df) >= 200 else df['ema50']

        current_close = float(df['close'].iloc[-1])
        ref_price = float(current_price) if (current_price and current_price > 0) else current_close
        ema20 = float(df['ema20'].iloc[-1])
        ema50 = float(df['ema50'].iloc[-1])
        ema200 = float(df['ema200'].iloc[-1])

        # Trend Determination
        if ref_price > ema20 > ema50:
            trend = "BULLISH"
        elif ref_price < ema20 < ema50:
            trend = "BEARISH"
        else:
            trend = "RANGING / MIXED"

        # 2. RSI (14)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi_series = 100 - (100 / (1 + rs))
        rsi = float(rsi_series.fillna(50).iloc[-1])

        # 3. ATR (14)
        high_low = df['high'] - df['low']
        high_cp = np.abs(df['high'] - df['close'].shift())
        low_cp = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().fillna(3.5).iloc[-1])

        # 4. Key Support & Resistance (strictly relative to ref_price)
        # Resistance levels must be ABOVE ref_price, sorted ascending (nearest first)
        recent_highs = [round(float(h), 2) for h in df['high'].tail(50) if float(h) > ref_price + 0.5]
        resistance_levels = sorted(list(set(recent_highs)))[:3]

        # Support levels must be BELOW ref_price, sorted descending (nearest first)
        recent_lows = [round(float(l), 2) for l in df['low'].tail(50) if float(l) < ref_price - 0.5]
        support_levels = sorted(list(set(recent_lows)), reverse=True)[:3]

        # Fallback if no swing high/low found
        if not resistance_levels:
            resistance_levels = [round(ref_price + (atr * 1.5), 2), round(ref_price + (atr * 3.0), 2)]
        if not support_levels:
            support_levels = [round(ref_price - (atr * 1.5), 2), round(ref_price - (atr * 3.0), 2)]

        # 5. Smart Money Concepts (SMC): FVG & Structure Break
        smc_info = TechnicalEngine._analyze_smc(df)

        # 6. Candle Range Theory (CRT): Asian Range & Liquidity Sweeps
        crt_info = TechnicalEngine._analyze_crt(df)

        return {
            "trend": trend,
            "rsi": round(rsi, 2),
            "atr": round(atr, 2),
            "ema20": round(ema20, 2),
            "ema50": round(ema50, 2),
            "ema200": round(ema200, 2),
            "support_levels": support_levels,
            "resistance_levels": resistance_levels,
            "smc": smc_info,
            "crt": crt_info
        }

    @staticmethod
    def _analyze_smc(df: pd.DataFrame) -> dict:
        """Analyzes Fair Value Gap (FVG / Imbalance) and Order Blocks."""
        if len(df) < 4:
            return {"structure": "NEUTRAL", "fvg_detected": False, "fvg_type": "NONE", "order_block": None}

        # Check latest completed candles for FVG (Candle 1, 2, 3)
        c1_high = df['high'].iloc[-3]
        c1_low = df['low'].iloc[-3]
        c3_high = df['high'].iloc[-1]
        c3_low = df['low'].iloc[-1]

        fvg_detected = False
        fvg_type = "NONE"
        fvg_level = 0.0

        # Bullish FVG: Candle 3 Low > Candle 1 High
        if c3_low > c1_high + 0.50:
            fvg_detected = True
            fvg_type = "BULLISH_IMBALANCE"
            fvg_level = round((c3_low + c1_high) / 2, 2)
        # Bearish FVG: Candle 3 High < Candle 1 Low
        elif c3_high < c1_low - 0.50:
            fvg_detected = True
            fvg_type = "BEARISH_IMBALANCE"
            fvg_level = round((c3_high + c1_low) / 2, 2)

        # Order Block detection (last opposite candle before strong move)
        ob_level = round(df['low'].tail(10).min(), 2) if fvg_type == "BULLISH_IMBALANCE" else round(df['high'].tail(10).max(), 2)

        return {
            "structure": "BULLISH_BOS" if fvg_type == "BULLISH_IMBALANCE" else ("BEARISH_BOS" if fvg_type == "BEARISH_IMBALANCE" else "RANGE"),
            "fvg_detected": fvg_detected,
            "fvg_type": fvg_type,
            "fvg_level": fvg_level,
            "order_block": ob_level
        }

    @staticmethod
    def _analyze_crt(df: pd.DataFrame) -> dict:
        """Analyzes Asian Range High/Low and Liquidity Sweep (Candle Range Theory)."""
        if len(df) < 24:
            return {"asian_high": 0.0, "asian_low": 0.0, "swept": "NONE"}

        # Approximate Asian range from 24 to 12 bars ago
        asian_segment = df.iloc[-24:-12]
        asian_high = round(float(asian_segment['high'].max()), 2)
        asian_low = round(float(asian_segment['low'].min()), 2)

        current_high = float(df['high'].iloc[-1])
        current_low = float(df['low'].iloc[-1])

        swept = "NONE"
        if current_high > asian_high:
            swept = "ASIAN_HIGH_SWEPT (Liquidity Grab Above)"
        elif current_low < asian_low:
            swept = "ASIAN_LOW_SWEPT (Liquidity Grab Below)"

        return {
            "asian_high": asian_high,
            "asian_low": asian_low,
            "swept": swept
        }

technical_engine = TechnicalEngine()
