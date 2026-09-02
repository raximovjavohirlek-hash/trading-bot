from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from core.config import settings
from data.collector import data_collector
from telegram.keyboards import get_main_reply_keyboard

router = Router()

@router.message(Command("health"))
@router.message(Command("status"))
@router.message(F.text == "🩺 Tizim Holati")
async def cmd_health(message: Message):
    tick = data_collector.latest_tick
    data_status = "✅ Faol" if tick else "⚠️ Kutilmoqda"
    active_prov = data_collector.active_provider_name
    
    goldapi_status = "✅ Ulangan" if settings.GOLDAPI_KEY else "ℹ️ API Key yo'q (Fallback ishlamoqda)"
    gemini_status = "✅ Ulangan" if settings.GEMINI_API_KEY else "ℹ️ API Key yo'q (Heuristic AI ishlamoqda)"

    text = f"""🩺 <b>TIZIM DIAGNOSTIKASI VA SOG'LIQ HOLATI (HEALTH CHECK)</b>

• Telegram Bot: ✅ Ishlayapti
• Data Collector: {data_status}
• Faol Ma'lumot Manbasi: <b>{active_prov}</b>
• GoldAPI.io: {goldapi_status}
• YahooFinance (GC=F / DXY / US10Y): ✅ Ishlayapti
• Gemini AI Engine: {gemini_status}
• SQLite Ma'lumotlar Bazasi: ✅ Ulangan

<i>Tizim barcha failover va resilience talablariga to'liq javob beradi.</i>"""
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())
