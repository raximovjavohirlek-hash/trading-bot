from __future__ import annotations
from typing import Dict, Any
from trading.risk_engine import risk_engine

class TradingSchemeEngine:
    """
    Generates institutional, mathematically sound trading plans (Savdo Sxemasi)
    based on Smart Money Concepts (SMC), Multi-Timeframe Alignment, ATR volatility,
    and institutional risk management.
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

        if score >= 2:
            direction = "BUY"
            action_text = "BUY (Sotib Olish / Long)"
            action_emoji = "🟢"
        elif score <= -2:
            direction = "SELL"
            action_text = "SELL (Sotish / Short)"
            action_emoji = "🔴"
        else:
            direction = "WAIT"
            action_text = "WAIT (Kutish va Tasdiqni Kuzatish)"
            action_emoji = "🟡"

        supports = tech_m15.get("support_levels", [])
        resistances = tech_m15.get("resistance_levels", [])
        order_block = smc.get("order_block")
        fvg_level = smc.get("fvg_level", 0.0)

        # 2. Compute Entry, Stop Loss, and Take Profits
        if direction == "BUY":
            # Entry Zone: Pullback to nearest Support / OB / FVG
            entry_low = supports[0] if (supports and supports[0] < price) else round(price - (atr * 0.6), 2)
            entry_high = round(min(price, entry_low + (atr * 0.4)), 2)
            if entry_low >= entry_high:
                entry_low = round(entry_high - 1.50, 2)

            entry_ref = round((entry_low + entry_high) / 2, 2)

            # Stop Loss strictly below Support / Structure
            sl_distance = max(atr * 1.2, 3.5)
            sl = round(entry_low - sl_distance, 2)
            risk_points = round(entry_ref - sl, 2)

            # Take Profits (1:1.5, 1:2.5, 1:4)
            tp1 = round(entry_ref + (risk_points * 1.5), 2)
            tp2 = round(entry_ref + (risk_points * 2.5), 2)
            tp3 = round(entry_ref + (risk_points * 4.0), 2)

            # If resistances exist above, align TPs
            if resistances and resistances[0] > entry_ref + 2.0:
                tp1 = min(tp1, resistances[0])

            invalidation = round(sl - 0.5, 2)
            strategy_type = "SMC Retest / Dip Buy (Korreksiyada kirish)"

        elif direction == "SELL":
            # Entry Zone: Retest of nearest Resistance / OB / FVG
            entry_high = resistances[0] if (resistances and resistances[0] > price) else round(price + (atr * 0.6), 2)
            entry_low = round(max(price, entry_high - (atr * 0.4)), 2)
            if entry_low >= entry_high:
                entry_high = round(entry_low + 1.50, 2)

            entry_ref = round((entry_low + entry_high) / 2, 2)

            # Stop Loss strictly above Resistance / Structure
            sl_distance = max(atr * 1.2, 3.5)
            sl = round(entry_high + sl_distance, 2)
            risk_points = round(sl - entry_ref, 2)

            # Take Profits
            tp1 = round(entry_ref - (risk_points * 1.5), 2)
            tp2 = round(entry_ref - (risk_points * 2.5), 2)
            tp3 = round(entry_ref - (risk_points * 4.0), 2)

            if supports and supports[0] < entry_ref - 2.0:
                tp1 = max(tp1, supports[0])

            invalidation = round(sl + 0.5, 2)
            strategy_type = "SMC Pullback / Sell the Rally (Korreksiyada sotish)"

        else: # WAIT
            entry_low = round(price - 2.0, 2)
            entry_high = round(price + 2.0, 2)
            entry_ref = price
            sl = round(price - 5.0, 2)
            risk_points = 5.0
            tp1 = round(price + 7.5, 2)
            tp2 = round(price + 12.5, 2)
            tp3 = round(price + 20.0, 2)
            invalidation = round(price - 6.0, 2)
            strategy_type = "Bozor konsolidatsiyada - Aniq signal kutilmoqda"

        # 3. Calculate Position Sizes
        lot_1k = risk_engine.calculate_lot_size(1000.0, 1.0, entry_ref, sl)["lots"]
        lot_5k = risk_engine.calculate_lot_size(5000.0, 1.0, entry_ref, sl)["lots"]
        lot_10k = risk_engine.calculate_lot_size(10000.0, 1.0, entry_ref, sl)["lots"]

        # Confluence checklist
        confluences = []
        if snapshot.get("is_killzone"):
            confluences.append(f"Faol Likvidlik: {snapshot.get('killzone_name')}")
        if smc.get("structure") != "NEUTRAL":
            confluences.append(f"SMC Tuzilma: {smc.get('structure')}")
        if crt.get("swept") != "NONE":
            confluences.append(f"CRT Likvidlik: {crt.get('swept')}")
        if snapshot.get("macro_bias") == direction:
            confluences.append(f"Makro Fon: DXY va Obligatsiyalar {direction} ni tasdiqlaydi")

        if not confluences:
            confluences.append("M15 Sham yopilishi va MFI/RSI tasdiqi talab qilinadi")

        return {
            "direction": direction,
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
            "tp1_rr": "1:1.5",
            "tp2": tp2,
            "tp2_rr": "1:2.5",
            "tp3": tp3,
            "tp3_rr": "1:4.0",
            "invalidation": invalidation,
            "lot_1k": lot_1k,
            "lot_5k": lot_5k,
            "lot_10k": lot_10k,
            "confluences": confluences,
            "session": snapshot.get("session", "Noma'lum")
        }

scheme_engine = TradingSchemeEngine()
