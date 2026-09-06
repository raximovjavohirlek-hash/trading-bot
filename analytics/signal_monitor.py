from __future__ import annotations
import asyncio
import time
from aiogram import Bot
from core.logger import logger
from core.database import db_manager
from analytics.snapshot_engine import snapshot_engine
from ai.ai_engine import ai_engine
from trading.scheme_engine import scheme_engine

class SignalMonitor:
    """
    Background automated monitoring service.
    Scans the market 24/7 for 100% factual high-probability (90-100/100) setups
    and automatically broadcasts them to Telegram subscribers.
    """
    def __init__(self):
        self.is_running = False
        self.bot: Bot = None
        self.last_alert_time = 0.0
        self.last_alert_direction = ""

    def set_bot(self, bot: Bot):
        self.bot = bot

    async def start(self):
        self.is_running = True
        logger.info("SignalMonitor background servisi ishga tushdi (90-100% signallarni avtomat monitoring qilish)...")
        # Initial sleep to allow collector to fetch first ticks
        await asyncio.sleep(15)

        while self.is_running:
            try:
                await self.check_for_high_probability_signal()
            except Exception as e:
                logger.error(f"SignalMonitor xatolik: {e}")

            # Check every 45 seconds
            await asyncio.sleep(45)

    async def check_for_high_probability_signal(self):
        if not self.bot:
            return

        snapshot = await snapshot_engine.generate_snapshot()
        ai_res = await ai_engine.analyze_market(snapshot)
        plan = scheme_engine.generate_plan(snapshot, ai_res)

        confidence = plan.get("confidence", 0)
        direction = plan.get("direction", "WAIT")
        now = time.time()

        # Trigger threshold: 90/100 or 100/100
        if confidence >= 90 and direction in ["BUY", "SELL"]:
            # Cooldown check: 45 minutes between duplicate alerts for same direction
            if direction == self.last_alert_direction and (now - self.last_alert_time) < 2700:
                return

            self.last_alert_time = now
            self.last_alert_direction = direction

            logger.info(f"🚨 YUQORI EHTIMOLLIKDAGI (A+) SIGNAL TOPILDI: {direction} | Ishonch: {confidence}/100")
            subscribers = await db_manager.get_subscribers()
            if not subscribers:
                logger.info("A+ Signal topildi, lekin obunachilar ro'yxati hali bo'sh (kamida 1 marta /start bosilishi kerak).")
                return

            text = self.format_high_prob_alert(snapshot, plan)

            # Broadcast to all registered subscribers
            for chat_id in subscribers:
                try:
                    await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
                except Exception as ex:
                    logger.warning(f"Foydalanuvchiga ({chat_id}) avtomat xabar yuborib bo'lmadi: {ex}")

            # Save alert to DB
            await db_manager.save_alert("HIGH_PROB_SIGNAL", f"{direction} {confidence}/100", "CRITICAL")

    def format_high_prob_alert(self, snapshot: dict, plan: dict) -> str:
        price = snapshot["price"]
        confluences = "\n✅ ".join(plan["confluences"])
        killzone = f"⚡ {snapshot['killzone_name']}" if snapshot["is_killzone"] else snapshot["session"]

        return f"""🚨 <b>AVTOMATIK INSTITUTIONAL SIGNAL ALERT! (A+ SETUP)</b>

🎯 <b>Ishonch darajasi:</b> <code>{plan['confidence']}/100 (ENG YUQORI FAKTIK EHTIMOLLIK)</code>
📌 <b>Joriy Spot Narxi:</b> <code>${price:.2f}</code>
{plan['action_emoji']} <b>Savdo Yo'nalishi:</b> <b>{plan['action_text']}</b>
📋 <b>Strategiya:</b> <i>{plan['strategy_type']}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━
🗺 <b>ANIQ SAVDO REJASI:</b>

<b>1. Kirish Zonasi:</b> <code>{plan['entry_range']}</code>
<b>2. Xavfsiz Stop Loss (SL):</b> <code>${plan['sl']:.2f}</code>
   └ <i>Risk masofasi: ${plan['sl_dollars']:.2f} (~{plan['sl_pips']} pip)</i>

<b>3. Aniq Maqsadlar (Take Profit):</b>
   • <b>TP 1:</b> <code>${plan['tp1']:.2f}</code> (50% yopish va Breakeven)
   • <b>TP 2:</b> <code>${plan['tp2']:.2f}</code> (Asosiy maqsad)
   • <b>TP 3:</b> <code>${plan['tp3']:.2f}</code> (Katta trend nishoni)

━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 <b>1% RISK BO'YICHA TAVSIYA ETILGAN LOT:</b>
   • $1,000 hisob:  <code>{plan['lot_1k']} Lot</code> (Risk: ~$10)
   • $5,000 hisob:  <code>{plan['lot_5k']} Lot</code> (Risk: ~$50)
   • $10,000 hisob: <code>{plan['lot_10k']} Lot</code> (Risk: ~$100)

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 <b>90-100% ISHONCH FAKTLARI (MATEMATIK VA INSTITUTIONAL TASDIQLAR):</b>
✅ {confluences}
• Faol Seans: {killzone}
❌ <b>Inkor darajasi:</b> <code>${plan['invalidation']:.2f}</code>

🛡 <i>Qat'iy qoida: Narx TP1 ga yetganda Stop Lossni kirish narxiga suring!</i>"""

    def stop(self):
        self.is_running = False
        logger.info("SignalMonitor to'xtatildi.")

signal_monitor = SignalMonitor()
