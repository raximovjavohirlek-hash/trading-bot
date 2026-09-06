from __future__ import annotations
from typing import Dict, Any
from trading.risk_engine import risk_engine

class TradingSchemeEngine:
    """
    Generates institutional, mathematically sound trading plans (Savdo Sxemasi)
    based on Smart Money Concepts (SMC), Candle Range Theory (CRT),
    and institutional risk management from the course textbooks.
    """

    @staticmethod
    def generate_plan(snapshot: dict, ai_res: dict) -> dict:
        price = float(snapshot["price"])
        tech_m15 = snapshot.get("tech_m15", {})
        tech_h1 = snapshot.get("tech_h1", {})
        smc = tech_m15.get("smc", {})
        crt = tech_m15.get("crt", {})
        atr = float(tech_m15.get("atr", 4.0))
        atr = max(2.5, min(atr, 15.0)) # boundary check

        ai_bias = ai_res.get("bias", "NEUTRAL")
        confidence = int(ai_res.get("confidence", 50))
        regime = snapshot.get("regime", "RANGING")
        macro_bias = snapshot.get("macro_bias", "NEUTRAL")

        # 1. Determine High-Probability Direction
        score = 0
        if ai_bias == "BULLISH": score += 2
        elif ai_bias == "BEARISH": score -= 2

        if "BULLISH" in regime: score += 1
        elif "BEARISH" in regime: score -= 1

        if macro_bias == "BULLISH": score += 1
        elif macro_bias == "BEARISH": score -= 1

        supports = tech_m15.get("support_levels", [])
        resistances = tech_m15.get("resistance_levels", [])

        # Key trigger levels for breakout/continuation
        break_high = resistances[0] if (resistances and resistances[0] > price) else round(price + (atr * 1.5), 2)
        break_low = supports[0] if (supports and supports[0] < price) else round(price - (atr * 1.5), 2)

        # Scenarios for conditional entry (WAIT mode)
        # Bullish Scenario: Break above break_high -> Retest
        b_entry_low = round(break_high - 0.8, 2)
        b_entry_high = round(break_high + 0.8, 2)
        b_entry_ref = round((b_entry_low + b_entry_high) / 2, 2)
        b_sl = round(b_entry_low - max(atr * 1.2, 3.5), 2)
        b_risk = round(b_entry_ref - b_sl, 2)
        b_tp1 = round(b_entry_ref + (b_risk * 1.5), 2)
        b_tp2 = round(b_entry_ref + (b_risk * 2.8), 2)

        # Bearish Scenario: Break below break_low -> Retest
        s_entry_high = round(break_low + 0.8, 2)
        s_entry_low = round(break_low - 0.8, 2)
        s_entry_ref = round((s_entry_high + s_entry_low) / 2, 2)
        s_sl = round(s_entry_high + max(atr * 1.2, 3.5), 2)
        s_risk = round(s_sl - s_entry_ref, 2)
        s_tp1 = round(s_entry_ref - (s_risk * 1.5), 2)
        s_tp2 = round(s_entry_ref - (s_risk * 2.8), 2)

        # Active trade determination
        if score >= 2 and confidence >= 60:
            direction = "BUY"
            action_text = "BUY (Sotib Olish / Long)"
            action_emoji = "🟢"
            is_active = True
        elif score <= -2 and confidence >= 60:
            direction = "SELL"
            action_text = "SELL (Sotish / Short)"
            action_emoji = "🔴"
            is_active = True
        else:
            direction = "WAIT"
            action_text = "WAIT (Kutish va Tasdiqni Kuzatish)"
            action_emoji = "🟡"
            is_active = False

        # Active Trade calculations (if is_active)
        if direction == "BUY":
            entry_low = supports[0] if (supports and supports[0] < price) else round(price - (atr * 0.6), 2)
            entry_high = round(min(price, entry_low + (atr * 0.4)), 2)
            if entry_low >= entry_high:
                entry_low = round(entry_high - 1.50, 2)
            entry_ref = round((entry_low + entry_high) / 2, 2)
            sl_distance = max(atr * 1.2, 3.5)
            sl = round(entry_low - sl_distance, 2)
            risk_points = round(entry_ref - sl, 2)
            tp1 = round(entry_ref + (risk_points * 1.5), 2)
            tp2 = round(entry_ref + (risk_points * 2.5), 2)
            tp3 = round(entry_ref + (risk_points * 4.0), 2)
            invalidation = round(sl - 0.5, 2)
            strategy_type = "SMC Retest / Dip Buy (Korreksiyada kirish)"
        elif direction == "SELL":
            entry_high = resistances[0] if (resistances and resistances[0] > price) else round(price + (atr * 0.6), 2)
            entry_low = round(max(price, entry_high - (atr * 0.4)), 2)
            if entry_low >= entry_high:
                entry_high = round(entry_low + 1.50, 2)
            entry_ref = round((entry_low + entry_high) / 2, 2)
            sl_distance = max(atr * 1.2, 3.5)
            sl = round(entry_high + sl_distance, 2)
            risk_points = round(sl - entry_ref, 2)
            tp1 = round(entry_ref - (risk_points * 1.5), 2)
            tp2 = round(entry_ref - (risk_points * 2.5), 2)
            tp3 = round(entry_ref - (risk_points * 4.0), 2)
            invalidation = round(sl + 0.5, 2)
            strategy_type = "SMC Pullback / Sell the Rally (Korreksiyada sotish)"
        else:
            entry_low = entry_high = entry_ref = price
            sl = round(price - 5.0, 2)
            risk_points = 5.0
            tp1 = tp2 = tp3 = invalidation = price
            strategy_type = "Bozor konsolidatsiyada - Diapazon chegaralari buzilishi kutilmoqda"

        # Position Sizing
        lot_1k = risk_engine.calculate_lot_size(1000.0, 1.0, entry_ref, sl)["lots"]
        lot_5k = risk_engine.calculate_lot_size(5000.0, 1.0, entry_ref, sl)["lots"]
        lot_10k = risk_engine.calculate_lot_size(10000.0, 1.0, entry_ref, sl)["lots"]

        confluences = []
        if snapshot.get("is_killzone"):
            confluences.append(f"Faol Likvidlik: {snapshot.get('killzone_name')}")
        if smc.get("structure") != "NEUTRAL":
            confluences.append(f"SMC Tuzilma: {smc.get('structure')}")
        if crt.get("swept") != "NONE":
            confluences.append(f"CRT Likvidlik: {crt.get('swept')}")
        if snapshot.get("macro_bias") == direction:
            confluences.append(f"Makro Fon: DXY va Obligatsiyalar {direction} ni tasdiqlaydi")

        return {
            "direction": direction,
            "is_active": is_active,
            "action_text": action_text,
            "action_emoji": action_emoji,
            "strategy_type": strategy_type,
            "confidence": confidence,
            "entry_range": f"${entry_low:.2f} - ${entry_high:.2f}",
            "entry_ref": entry_ref,
            "sl": sl,
            "sl_pips": round(risk_points * 10, 1),
            "sl_dollars": risk_points,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "invalidation": invalidation,
            "lot_1k": lot_1k,
            "lot_5k": lot_5k,
            "lot_10k": lot_10k,
            "confluences": confluences,
            "session": snapshot.get("session", "Noma'lum"),
            # Conditional Scenarios
            "break_high": break_high,
            "break_low": break_low,
            "b_entry": f"${b_entry_low:.2f} - ${b_entry_high:.2f}",
            "b_sl": b_sl,
            "b_risk_pips": round(b_risk * 10, 1),
            "b_tp1": b_tp1,
            "b_tp2": b_tp2,
            "s_entry": f"${s_entry_low:.2f} - ${s_entry_high:.2f}",
            "s_sl": s_sl,
            "s_risk_pips": round(s_risk * 10, 1),
            "s_tp1": s_tp1,
            "s_tp2": s_tp2
        }

scheme_engine = TradingSchemeEngine()
