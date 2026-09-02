from datetime import datetime, timezone

class MacroEngine:
    def __init__(self):
        pass

    @staticmethod
    def get_current_session() -> dict:
        """
        Determines current trading session and Killzones (UTC & UZT).
        Asian Session: 00:00 - 08:00 UTC (05:00 - 13:00 UZT)
        London Session (Killzone): 07:00 - 10:00 UTC (12:00 - 15:00 UZT)
        NY Killzone / Overlap: 12:00 - 16:00 UTC (17:00 - 21:00 UZT)
        """
        now_utc = datetime.now(timezone.utc)
        hour = now_utc.hour
        
        sessions = []
        is_killzone = False
        killzone_name = "None"
        
        # Asian session
        if 0 <= hour < 8:
            sessions.append("Asian Session")
        # London session
        if 7 <= hour < 16:
            sessions.append("London Session")
            if 7 <= hour <= 10:
                is_killzone = True
                killzone_name = "London Open Killzone"
        # New York session
        if 12 <= hour < 21:
            sessions.append("New York Session")
            if 12 <= hour <= 15:
                is_killzone = True
                killzone_name = "NY Open / London Overlap Killzone"
                
        session_str = " + ".join(sessions) if sessions else "Off-Hours / Asian Quiet"
        
        return {
            "session": session_str,
            "is_killzone": is_killzone,
            "killzone_name": killzone_name,
            "utc_time": now_utc.strftime("%H:%M UTC")
        }

    @staticmethod
    def evaluate_macro_bias(dxy_change: float, us10y_change: float, real_yield: float) -> dict:
        """
        Gold is inversely correlated with DXY & Real Yields.
        If DXY falls and Real Yield falls -> Bullish for Gold.
        If DXY rises and Real Yield rises -> Bearish for Gold.
        """
        score = 0
        reasons = []

        if dxy_change < -0.10:
            score += 2
            reasons.append("DXY pasaymoqda (Dollar zaiflashmoqda, Oltin uchun Bullish)")
        elif dxy_change > 0.10:
            score -= 2
            reasons.append("DXY ko'tarilmoqda (Dollar kuchaymoqda, Oltin uchun Bearish)")
        else:
            reasons.append("DXY neytral diapazonda")

        if us10y_change < -0.02:
            score += 1
            reasons.append("US10Y rentabelligi tushmoqda (Bullish)")
        elif us10y_change > 0.02:
            score -= 1
            reasons.append("US10Y rentabelligi oshmoqda (Bearish)")

        if real_yield < 2.0:
            score += 1
            reasons.append("Real Yields past darajada (Bullish catalyst)")
        elif real_yield > 2.5:
            score -= 1
            reasons.append("Real Yields yuqori darajada (Bearish headwind)")

        if score >= 2:
            bias = "BULLISH"
        elif score <= -2:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        return {
            "macro_bias": bias,
            "macro_score": score,
            "macro_reasons": reasons
        }

macro_engine = MacroEngine()
