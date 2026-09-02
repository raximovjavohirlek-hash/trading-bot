from __future__ import annotations
import json
import time
from typing import Optional, Dict, Any
import google.generativeai as genai
from core.config import settings
from core.logger import logger
from core.database import db_manager
from ai.prompt_templates import SYSTEM_PROMPT, build_market_prompt

class AIEngine:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self._cached_analysis: Optional[Dict[str, Any]] = None
        self._cached_time: float = 0.0

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None
            logger.info("GEMINI_API_KEY o'rnatilmagan. Heuristic AI fallback ishlaydi.")

    async def analyze_market(self, snapshot: dict, force: bool = False) -> Dict[str, Any]:
        """
        Analyzes market snapshot using Gemini AI or heuristic fallback.
        Enforces caching to optimize API costs (TZ Section 46 & 47).
        """
        now = time.time()
        # 30 min caching unless forced
        if not force and self._cached_analysis and (now - self._cached_time) < (settings.AI_MIN_INTERVAL_MINUTES * 60):
            return self._cached_analysis

        if self.model and self.api_key:
            try:
                prompt_text = build_market_prompt(snapshot)
                response = self.model.generate_content(
                    contents=[{"role": "user", "parts": [SYSTEM_PROMPT, prompt_text]}],
                    generation_config={"temperature": 0.2, "top_p": 0.8}
                )
                raw_text = response.text.strip()
                # Parse JSON
                cleaned_json = raw_text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(cleaned_json)
                
                # Save to DB
                await db_manager.save_ai_analysis(
                    bias=parsed.get("bias", "NEUTRAL"),
                    confidence=parsed.get("confidence", 50),
                    reasons=parsed.get("main_reasons", []),
                    counter_evidence=parsed.get("counter_evidence", []),
                    invalidation_price=parsed.get("invalidation_price", 0.0),
                    status=parsed.get("status", "WAIT FOR CONFIRMATION"),
                    raw_response=raw_text
                )
                
                self._cached_analysis = parsed
                self._cached_time = now
                return parsed

            except Exception as e:
                logger.error(f"Gemini API tahlilida xatolik: {e}, Heuristic fallbackga o'tilmoqda...")

        # Fallback Heuristic Analysis
        fallback_res = self._heuristic_analysis(snapshot)
        self._cached_analysis = fallback_res
        self._cached_time = now
        return fallback_res

    def _heuristic_analysis(self, snapshot: dict) -> Dict[str, Any]:
        """Rule-based quantitative fallback when AI key is absent or API fails."""
        price = snapshot["price"]
        regime = snapshot["regime"]
        macro_bias = snapshot["macro_bias"]
        tech_m15 = snapshot.get("tech_m15", {})
        rsi = tech_m15.get("rsi", 50.0)
        atr = tech_m15.get("atr", 3.5)

        reasons = []
        counter = []
        score = 0

        if macro_bias == "BULLISH":
            score += 25
            reasons.append("DXY pasayishi va makro ko'rsatkichlar Oltinni qo'llab-quvvatlamoqda.")
        elif macro_bias == "BEARISH":
            score -= 25
            reasons.append("DXY kuchayishi Oltin narxiga bosim o'tkazmoqda.")

        if "BULLISH" in regime:
            score += 35
            reasons.append("Multi-timeframe trend yo'nalishi yuqoriga (Bullish Structure).")
        elif "BEARISH" in regime:
            score -= 35
            reasons.append("Multi-timeframe trend yo'nalishi pastga (Bearish Structure).")

        if rsi > 70:
            score -= 10
            counter.append("RSI overbought (o'ta sotib olingan) zonasida, qisqa muddatli korreksiya xavfi bor.")
        elif rsi < 30:
            score += 10
            counter.append("RSI oversold zonasida.")

        if snapshot.get("is_killzone"):
            reasons.append(f"Hozir {snapshot.get('killzone_name')} seansi. Likvidlik yuqori.")
        else:
            counter.append("Seans o'rtasidagi past likvidlik bosqichi.")

        if score >= 35:
            bias = "BULLISH"
            confidence = min(60 + score // 2, 85)
            invalidation = round(price - (atr * 2.5), 2)
            status = "MONITOR_BREAKOUT"
        elif score <= -35:
            bias = "BEARISH"
            confidence = min(60 + abs(score) // 2, 85)
            invalidation = round(price + (atr * 2.5), 2)
            status = "MONITOR_BREAKOUT"
        else:
            bias = "NEUTRAL"
            confidence = 50
            invalidation = round(price - 10.0, 2)
            status = "WAIT FOR CONFIRMATION"

        return {
            "bias": bias,
            "confidence": confidence,
            "main_reasons": reasons,
            "counter_evidence": counter,
            "invalidation_price": invalidation,
            "status": status,
            "summary_uz": f"Bozor hozirda {bias} holatida ({confidence}/100 ishonch). Bekor bo'lish darajasi: ${invalidation}."
        }

ai_engine = AIEngine()
