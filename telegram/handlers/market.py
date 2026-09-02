from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from analytics.snapshot_engine import snapshot_engine
from ai.ai_engine import ai_engine
from telegram.formatters import (
    format_dashboard, format_gold_snapshot, format_technical_report, format_macro_report, format_trading_scheme
)
from telegram.keyboards import get_dashboard_inline_keyboard, get_main_reply_keyboard

router = Router()

@router.message(Command("scheme"))
@router.message(F.text == "🎯 Savdo Sxemasi")
async def show_scheme(message: Message):
    msg = await message.answer("⏳ <i>Real-time bozor sxemasi va savdo rejasi tuzilmoqda...</i>", parse_mode="HTML")
    snapshot = await snapshot_engine.generate_snapshot()
    ai_res = await ai_engine.analyze_market(snapshot)
    text = format_trading_scheme(snapshot, ai_res)
    await msg.edit_text(text, parse_mode="HTML")

@router.message(Command("gold"))
@router.message(F.text == "🟡 Oltin Narxi")
async def cmd_gold(message: Message):
    snapshot = await snapshot_engine.generate_snapshot()
    text = format_gold_snapshot(snapshot)
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())

@router.message(Command("dashboard"))
@router.message(F.text == "📊 Dashboard")
async def cmd_dashboard(message: Message):
    snapshot = await snapshot_engine.generate_snapshot()
    text = format_dashboard(snapshot)
    await message.answer(text, parse_mode="HTML", reply_markup=get_dashboard_inline_keyboard())

@router.message(Command("technical"))
@router.message(F.text == "📈 Texnik Tahlil")
async def cmd_technical(message: Message):
    snapshot = await snapshot_engine.generate_snapshot()
    text = format_technical_report(snapshot)
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())

@router.message(Command("macro"))
@router.message(F.text == "🌐 Makro Tahlil")
async def cmd_macro(message: Message):
    snapshot = await snapshot_engine.generate_snapshot()
    text = format_macro_report(snapshot)
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())

@router.message(Command("regime"))
@router.message(F.text == "⚡ Bozor Rejimi")
async def cmd_regime(message: Message):
    snapshot = await snapshot_engine.generate_snapshot()
    regime = snapshot["regime"].replace("_", " ")
    desc = snapshot["regime_description"]
    vol = snapshot["volatility"].replace("_", " ")
    killzone = snapshot["killzone_name"]

    text = f"""⚡ <b>BOZOR REJIMI VA O'ZGARUVCHANLIK (REGIME ENGINE)</b>

• Hozirgi Rejim: <b>{regime}</b>
• Tavsif: <i>{desc}</i>
• Volatillik (O'zgaruvchanlik): <b>{vol}</b>
• Seans Holati: <b>{snapshot['session']}</b>
• Killzone: <b>{killzone}</b>"""
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())

# Callback Query Handlers
@router.callback_query(F.data == "act_scheme")
async def cb_scheme(call: CallbackQuery):
    await call.answer()
    snapshot = await snapshot_engine.generate_snapshot()
    ai_res = await ai_engine.analyze_market(snapshot)
    text = format_trading_scheme(snapshot, ai_res)
    await call.message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "act_refresh_dash")
async def cb_refresh_dash(call: CallbackQuery):
    await call.answer("Yangilandi!")
    snapshot = await snapshot_engine.generate_snapshot()
    text = format_dashboard(snapshot)
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_dashboard_inline_keyboard())
    except Exception:
        pass
