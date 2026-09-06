from datetime import datetime, timezone
from trading.risk_engine import risk_engine
from trading.scheme_engine import scheme_engine

def format_dashboard(snapshot: dict) -> str:
    """
    Renders real-time Gold Market Monitoring Dashboard matching TZ Section 54.
    """
    price = snapshot["price"]
    dxy = snapshot["dxy"]
    us10y = snapshot["us10y"]
    real_yield = snapshot["real_yield"]
    regime = snapshot["regime"].replace("_", " ")
    volatility = snapshot["volatility"].replace("_", " ")
    htf = snapshot["htf_trend"]
    ltf = snapshot["ltf_trend"]
    session = snapshot["session"]
    killzone = f"⚡ {snapshot['killzone_name']}" if snapshot["is_killzone"] else "Yo'q"

    # Timeframe directional indicators
    t_m15 = "↑" if ltf == "BULLISH" else ("↓" if ltf == "BEARISH" else "→")
    t_h1 = "↑" if htf == "BULLISH" else ("↓" if htf == "BEARISH" else "→")

    return f"""<b>┌──────────────────────────────────────────┐</b>
<b>│           GOLD MARKET INTELLIGENCE       │</b>
<b>├──────────────────────────────────────────┤</b>
<b>│ XAUUSD       ${price:.2f}</b>
<b>│ DXY          {dxy:.2f}</b>
<b>│ US10Y        {us10y:.3f}%</b>
<b>│ Real Yield   {real_yield:.3f}%</b>
<b>├──────────────────────────────────────────┤</b>
<b>│ MARKET REGIME: {regime}</b>
<b>├──────────────────────────────────────────┤</b>
<b>│ 15M Trend:    {t_m15} {ltf}</b>
<b>│ 1H Trend:     {t_h1} {htf}</b>
<b>├──────────────────────────────────────────┤</b>
<b>│ VOLATILITY:   {volatility}</b>
<b>│ SEANS:        {session}</b>
<b>│ KILLZONE:     {killzone}</b>
<b>└──────────────────────────────────────────┘</b>

<i>Yangilangan vaqt: {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')} | Manba: {snapshot.get('source')}</i>"""

def format_gold_snapshot(snapshot: dict) -> str:
    price = snapshot["price"]
    bid = snapshot["bid"]
    ask = snapshot["ask"]
    spread = snapshot["spread"]
    ch = snapshot["change"]
    chp = snapshot["change_percent"]
    belgi = "📈" if ch >= 0 else "📉"

    return f"""🟡 <b>OLTIN (XAUUSD) REAL-TIME NARXI</b>

Hozirgi narx: <b>${price:.2f}</b>
Sotib olish (Bid): ${bid:.2f}
Sotish (Ask): ${ask:.2f}
Spred: ${spread:.2f}

Bugungi ochilish: ${snapshot['open']:.2f}
Bugungi eng yuqori (High): ${snapshot['high']:.2f}
Bugungi eng past (Low): ${snapshot['low']:.2f}

{belgi} Bugungi o'zgarish: {ch:+.2f} ({chp:+.2f}%)
🌐 Manba: <i>{snapshot.get('source')}</i>"""

def format_technical_report(snapshot: dict) -> str:
    tech_m15 = snapshot.get("tech_m15", {})
    tech_h1 = snapshot.get("tech_h1", {})
    smc = tech_m15.get("smc", {})
    crt = tech_m15.get("crt", {})

    supports = ", ".join([f"${s}" for s in tech_m15.get("support_levels", [])]) or "Yo'q"
    resistances = ", ".join([f"${r}" for r in tech_m15.get("resistance_levels", [])]) or "Yo'q"

    return f"""📊 <b>MULTIFRAME TEXNIK & INSTITUTIONAL (SMC/CRT) TAHLIL</b>

<b>15-Daqiqalik (M15) Ko'rsatkichlar:</b>
• Trend: <b>{tech_m15.get('trend')}</b>
• RSI (14): <b>{tech_m15.get('rsi')}</b>
• ATR (14): <b>${tech_m15.get('atr')}</b>
• EMA 20: ${tech_m15.get('ema20')} | EMA 50: ${tech_m15.get('ema50')}

<b>1-Soatlik (H1) Trend:</b> <b>{tech_h1.get('trend')}</b>

<b>🏛 Smart Money Concepts (SMC):</b>
• Tuzilma: <b>{smc.get('structure')}</b>
• Imbalance (FVG): <b>{smc.get('fvg_type')}</b> (Daraja: ${smc.get('fvg_level', 0)})
• Key Order Block: <b>${smc.get('order_block')}</b>

<b>🕯 Candle Range Theory (CRT):</b>
• Asian High: ${crt.get('asian_high')} | Asian Low: ${crt.get('asian_low')}
• Likvidlik holati: <i>{crt.get('swept')}</i>

<b>📍 Muhim Darajalar:</b>
• Qarshilik (Resistance): {resistances}
• Qo'llab-quvvatlash (Support): {supports}"""

def format_macro_report(snapshot: dict) -> str:
    reasons_str = "\n• ".join(snapshot.get("macro_reasons", []))
    return f"""🌐 <b>MAKROIQ TISODIY VA INTERMARKET TAHLILI</b>

• DXY (Dollar Indeksi): <b>{snapshot['dxy']:.2f}</b> ({snapshot['dxy_change']:+.2f})
• US10Y (10 yillik obligatsiyalar): <b>{snapshot['us10y']:.3f}%</b> ({snapshot['us10y_change']:+.2f})
• US Real Yield (Grafik rentabellik): <b>{snapshot['real_yield']:.3f}%</b>

<b>Makro Bias:</b> <b>{snapshot['macro_bias']}</b>

<b>Asosiy omillar:</b>
• {reasons_str}"""

def format_ai_report(ai_res: dict) -> str:
    bias = ai_res.get("bias", "NEUTRAL")
    confidence = ai_res.get("confidence", 50)
    reasons = "\n• ".join(ai_res.get("main_reasons", []))
    counter = "\n• ".join(ai_res.get("counter_evidence", []))
    invalidation = ai_res.get("invalidation_price", 0.0)
    status = ai_res.get("status", "WAIT FOR CONFIRMATION")
    summary = ai_res.get("summary_uz", "")

    bias_emoji = "🟢" if bias == "BULLISH" else ("🔴" if bias == "BEARISH" else "🟡")

    return f"""🤖 <b>AI MARKET INTELLIGENCE TAHLILI</b>

{bias_emoji} Yo'nalish (Bias): <b>{bias}</b>
🎯 Ishonch Darajasi (Confidence): <b>{confidence}/100</b>
📋 Tizim Holati (Status): <code>{status}</code>

<b>Asosiy Dalillar (Evidence):</b>
• {reasons}

<b>Qarama-Qarshi Xavflar (Counter Evidence):</b>
• {counter}

❌ <b>Inkor Etilish Darajasi (Invalidation Level):</b> <code>${invalidation}</code>

💡 <b>Xulosa:</b>
<i>{summary}</i>

⚠️ <i>Eslatma: AI maslahat bermaydi, faqat mavjud ko'rsatkichlar ehtimolini baholaydi.</i>"""

def format_trading_scheme(snapshot: dict, ai_res: dict) -> str:
    """
    Renders an institutional, mathematically consistent Gold Trading Scheme & Action Plan.
    Separates active high-probability setups from conditional WAIT scenarios.
    """
    plan = scheme_engine.generate_plan(snapshot, ai_res)
    price = snapshot["price"]
    killzone_status = f"⚡ {snapshot['killzone_name']}" if snapshot["is_killzone"] else "Oddiy vaqt"

    if not plan["is_active"]:
        # WAIT / LOW CONFIDENCE MODE -> CONDITIONAL BREAKOUT / RETEST SCENARIOS
        return f"""🎯 <b>INSTITUTIONAL SAVDO SXEMASI (TRADING ACTION PLAN)</b>

📌 <b>Joriy Spot Narxi:</b> <code>${price:.2f}</code>
🟡 <b>Tavsiya qilingan Holat:</b> <b>KUTISH (NO-TRADE / WAIT ZONE)</b>
🎯 <b>Ishonch darajasi:</b> <code>{plan['confidence']}/100 (Yuqori Risk / Noaniqlik)</code>
📋 <b>Bozor Holati:</b> <i>Konsolidatsiya diapazoni (Range) va Likvidlik to'planishi</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ <b>DARSLIK BO'YICHA TAHLIL VA XAVF (INDUCEMENT TRAP):</b>
<i>SMC va Bank Manipulyatsiyasi darsliklariga ko'ra, bozor diapazon o'rtasida turganda shoshilib savdoga kirish — banklar tuzog'iga (Inducement Trap) tushish demakdir. Hozir ikkala tomondagi likvidlik ovlanmoqda, shuning uchun chegaralar buzilmaguncha pozitsiya ochish qat'iyan man etiladi!</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━
🚦 <b>QACHON VA QANDAY RAQAMLARDA KIRISH KERAK (TRIGGERLAR):</b>

🟢 <b>1-SSENARIY: BUY (LONG) UCHUN ANIQ SHARTLAR</b>
• <b>Tasdiq (Trigger):</b> Narx <code>${plan['break_high']:.2f}</code> dan yuqoriga chiqib, kamida M15 sham tana (body) bilan yopilishi (BOS) shart.
• <b>Kutiladigan Kirish Zonasi:</b> <code>{plan['b_entry']}</code> (Retest vaqtida)
• <b>Xavfsiz Stop Loss (SL):</b> <code>${plan['b_sl']:.2f}</code> (~{plan['b_risk_pips']} pip)
• <b>Maqsadlar:</b> TP1: <code>${plan['b_tp1']:.2f}</code> | TP2: <code>${plan['b_tp2']:.2f}</code>

🔴 <b>2-SSENARIY: SELL (SHORT) UCHUN ANIQ SHARTLAR</b>
• <b>Tasdiq (Trigger):</b> Narx <code>${plan['break_low']:.2f}</code> dan pastga tushib, kamida M15 sham tana bilan yopilishi (BOS) shart.
• <b>Kutiladigan Kirish Zonasi:</b> <code>{plan['s_entry']}</code> (Retest vaqtida)
• <b>Xavfsiz Stop Loss (SL):</b> <code>${plan['s_sl']:.2f}</code> (~{plan['s_risk_pips']} pip)
• <b>Maqsadlar:</b> TP1: <code>${plan['s_tp1']:.2f}</code> | TP2: <code>${plan['s_tp2']:.2f}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡 <b>QAT'IY QOIDA:</b>
<i>Ushbu 2 ta darajadan biri M15 sham bilan buzilib tasdiqlanmaguncha bozorga mutlaqo kirmang. Shoshilmasdan tasdiqni kuting!</i>"""

    # ACTIVE SETUP (When confidence >= 60 and clear trend exists)
    confluences_str = "\n• ".join(plan["confluences"])
    return f"""🎯 <b>INSTITUTIONAL SAVDO SXEMASI (TRADING ACTION PLAN)</b>

📌 <b>Joriy Spot Narxi:</b> <code>${price:.2f}</code>
{plan['action_emoji']} <b>Tavsiya qilingan Yo'nalish:</b> <b>{plan['action_text']}</b>
📋 <b>Strategiya:</b> <i>{plan['strategy_type']}</i>
🎯 <b>Ishonch darajasi:</b> <code>{plan['confidence']}/100</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺 <b>QADAM-BA-QADAM SAVDO REJASI:</b>

<b>1. Kirish Zonasi (Entry Range):</b> <code>{plan['entry_range']}</code>
<b>2. Xavfsiz Stop Loss (SL):</b> <code>${plan['sl']:.2f}</code>
   └ <i>Risk masofasi: ${plan['sl_dollars']:.2f} (~{plan['sl_pips']} pip)</i>

<b>3. Bosqichma-bosqich Maqsadlar (Take Profit):</b>
   • <b>TP 1:</b> <code>${plan['tp1']:.2f}</code> (50% yopish va Breakeven)
   • <b>TP 2:</b> <code>${plan['tp2']:.2f}</code> (Asosiy maqsad)
   • <b>TP 3:</b> <code>${plan['tp3']:.2f}</code> (Trend davomi)

━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 <b>RISK VA POZITSIYA HAJMI (1% Risk bo'yicha):</b>
   • $1,000 hisob uchun:  <code>{plan['lot_1k']} Lot</code> (Risk: ~$10)
   • $5,000 hisob uchun:  <code>{plan['lot_5k']} Lot</code> (Risk: ~$50)
   • $10,000 hisob uchun: <code>{plan['lot_10k']} Lot</code> (Risk: ~$100)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>TASDIQLOVCHI FAKTORLAR (CONFLUENCES):</b>
• Seans: {plan['session']} ({killzone_status})
• {confluences_str}
❌ <b>Inkor darajasi (Invalidation):</b> <code>${plan['invalidation']:.2f}</code>

🛡 <b>SAVDONI BOSHQARISH QOIDASI:</b>
<i>Narx TP1 ga yetganida pozitsiyaning 50% qismini foyda bilan yoping va Stop Loss darajasini kirish narxiga (Breakeven) suring!</i>"""
