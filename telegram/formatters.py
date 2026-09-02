from datetime import datetime, timezone
from trading.risk_engine import risk_engine

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
    Renders a complete, step-by-step Trading Scheme & Action Plan.
    """
    price = snapshot["price"]
    tech_m15 = snapshot.get("tech_m15", {})
    atr = tech_m15.get("atr", 3.5)
    bias = ai_res.get("bias", "NEUTRAL")
    confidence = ai_res.get("confidence", 50)
    invalidation = ai_res.get("invalidation_price", price - 10.0)

    # Determine Scenario
    if bias == "BULLISH":
        action = "BUY (Sotib Olish)"
        entry_zone = f"${price - 1.50:.2f} - ${price:.2f}"
        sl = round(min(invalidation, price - (atr * 1.8)), 2)
        tp1 = round(price + (atr * 2.0), 2)
        tp2 = round(price + (atr * 3.5), 2)
        risk_lot = risk_engine.calculate_lot_size(10000.0, 1.0, price, sl)
        action_emoji = "🟢"
    elif bias == "BEARISH":
        action = "SELL (Sotish)"
        entry_zone = f"${price:.2f} - ${price + 1.50:.2f}"
        sl = round(max(invalidation, price + (atr * 1.8)), 2)
        tp1 = round(price - (atr * 2.0), 2)
        tp2 = round(price - (atr * 3.5), 2)
        risk_lot = risk_engine.calculate_lot_size(10000.0, 1.0, price, sl)
        action_emoji = "🔴"
    else:
        action = "WAIT / KUTISH (Kuzatuv rejimida)"
        entry_zone = "Kutish tavsiya etiladi"
        sl = round(price - 10.0, 2)
        tp1 = round(price + 10.0, 2)
        tp2 = round(price + 20.0, 2)
        risk_lot = {"lots": 0.01}
        action_emoji = "🟡"

    killzone_status = f"⚡ {snapshot['killzone_name']}" if snapshot["is_killzone"] else "Oddiy vaqt"

    return f"""🎯 <b>BOZOR XO'LATI VA HAMMASI QADAM-BA-QADAM SAVDO SXEMASI</b>

📌 <b>Hozirgi Narx:</b> <code>${price:.2f}</code>
{action_emoji} <b>Tavsiya qilingan yo'nalish:</b> <b>{action}</b>
🎯 <b>Ishonch darajasi:</b> <code>{confidence}/100</code>

---
🗺 <b>QADAM-BA-QADAM SXEMA (ACTION PLAN):</b>

<b>1. Kirish Zonasi (Entry Range):</b> <code>{entry_zone}</code>
<b>2. Xavfsiz Stop Loss (SL):</b> <code>${sl:.2f}</code> (Risk: ~{abs(round(price-sl, 2))} pip)
<b>3. Birinchi Maqsad (TP1):</b> <code>${tp1:.2f}</code> (1:2 Risk/Reward)
<b>4. Ikkinchi Maqsad (TP2):</b> <code>${tp2:.2f}</code> (1:3 Risk/Reward)
<b>5. Hisoblangan Lot Size ($10k balans, 1% risk):</b> <code>{risk_lot['lots']} Lot</code>

---
⚡ <b>TASDIQLASH QOIDALARI (Confirmation Rules):</b>
• <b>Seans:</b> {snapshot['session']} ({killzone_status})
• <b>M15 Sham:</b> Kamida 15 minutlik sham mo'ljallangan yo'nalishda yopilishi kerak.
• <b>Inkor bo'lish darajasi (Invalidation):</b> Narx <code>${invalidation}</code> ga yetsa, sxema bekor qilinadi.

⚠️ <i>Savdoga kirmasdan oldin riskni to'g'ri boshqaring!</i>"""
