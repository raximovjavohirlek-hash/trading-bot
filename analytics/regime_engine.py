class RegimeEngine:
    def __init__(self):
        pass

    @staticmethod
    def classify_regime(tech_m15: dict, tech_h1: dict, macro_data: dict, session_info: dict) -> dict:
        """
        Classifies current Gold Market Regime.
        """
        trend_m15 = tech_m15.get("trend", "NEUTRAL")
        trend_h1 = tech_h1.get("trend", "NEUTRAL")
        rsi = tech_m15.get("rsi", 50.0)
        atr = tech_m15.get("atr", 3.5)
        macro_bias = macro_data.get("macro_bias", "NEUTRAL")
        is_killzone = session_info.get("is_killzone", False)

        # Volatility assessment
        if atr > 8.0 or rsi > 75 or rsi < 25:
            volatility = "EXTREME_VOLATILITY"
        elif atr > 4.5:
            volatility = "HIGH_VOLATILITY"
        elif atr < 2.0:
            volatility = "LOW_VOLATILITY"
        else:
            volatility = "MODERATE_VOLATILITY"

        # Market Regime Classification
        if trend_m15 == "BULLISH" and trend_h1 == "BULLISH" and macro_bias != "BEARISH":
            regime = "STRONG_BULLISH_TREND"
            regime_desc = "Kuchli Bullish trend. DXY pasaymoqda va haridorlar bosimi yuqori."
        elif trend_m15 == "BEARISH" and trend_h1 == "BEARISH" and macro_bias != "BULLISH":
            regime = "STRONG_BEARISH_TREND"
            regime_desc = "Kuchli Bearish trend. DXY kuchaymoqda va sotuvchilar bosimi yuqori."
        elif trend_m15 != trend_h1:
            regime = "TIMEFRAME_DIVERGENCE"
            regime_desc = "Vaqt ramkalari ziddiyati (M15 va H1 ziddiyatli). Konsolidatsiya kutish tavsiya etiladi."
        elif volatility == "LOW_VOLATILITY":
            regime = "RANGE_ACCUMULATION"
            regime_desc = "Osiyo diapazoni / Jamlanish (PO3 Accumulation). Breakout kutilmoqda."
        elif volatility == "EXTREME_VOLATILITY":
            regime = "NEWS_VOLATILITY_SPIKE"
            regime_desc = "Yuqori o'zgaruvchanlik / Yangiliklar ta'siri. Xavf darajasi YUQORI."
        else:
            regime = "SIDEWAYS_CONSOLIDATION"
            regime_desc = "Yonlama harakat / Tor konsolidatsiya."

        return {
            "regime": regime,
            "regime_description": regime_desc,
            "volatility": volatility,
            "htf_trend": trend_h1,
            "ltf_trend": trend_m15,
            "is_killzone": is_killzone,
            "killzone_name": session_info.get("killzone_name", "None")
        }

regime_engine = RegimeEngine()
