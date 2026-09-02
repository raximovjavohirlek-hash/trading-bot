from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from analytics.snapshot_engine import snapshot_engine
from ai.ai_engine import ai_engine
from telegram.formatters import format_ai_report, format_technical_report
from telegram.keyboards import get_ai_inline_keyboard, get_main_reply_keyboard

router = Router()

@router.message(Command("ai_analysis"))
@router.message(F.text == "🤖 AI Analiz")
async def cmd_ai_analysis(message: Message):
    msg = await message.answer("⏳ <i>Gemini AI ma'lumotlar snapshotini tahlil qilmoqda...</i>", parse_mode="HTML")
    try:
        snapshot = await snapshot_engine.generate_snapshot()
        ai_res = await ai_engine.analyze_market(snapshot, force=True)
        text = format_ai_report(ai_res)
        await msg.edit_text(text, parse_mode="HTML", reply_markup=get_ai_inline_keyboard())
    except Exception as e:
        await msg.edit_text(f"⚠️ AI tahlilida xatolik: {e}")

@router.message(Command("research"))
async def cmd_research(message: Message):
    snapshot = await snapshot_engine.generate_snapshot()
    ai_res = await ai_engine.analyze_market(snapshot)
    text = f"""🔬 <b>RESEARCH MODE & HYPOTHESIS TESTING</b>

Current Hypothesis Bias: <b>{ai_res.get('bias')}</b>
Confidence Score: <b>{ai_res.get('confidence')}/100</b>
Invalidation Price: <b>${ai_res.get('invalidation_price')}</b>

Paper Trading sinovi uchun pastdagi <b>📝 Paper Trade</b> tugmasini bosing."""
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())

# Callbacks
@router.callback_query(F.data == "act_ai")
async def cb_ai(call: CallbackQuery):
    await call.answer()
    snapshot = await snapshot_engine.generate_snapshot()
    ai_res = await ai_engine.analyze_market(snapshot)
    text = format_ai_report(ai_res)
    await call.message.answer(text, parse_mode="HTML", reply_markup=get_ai_inline_keyboard())

@router.callback_query(F.data == "act_tech")
async def cb_tech(call: CallbackQuery):
    await call.answer()
    snapshot = await snapshot_engine.generate_snapshot()
    text = format_technical_report(snapshot)
    await call.message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "act_ai_force")
async def cb_ai_force(call: CallbackQuery):
    await call.answer("Yangilanmoqda...")
    snapshot = await snapshot_engine.generate_snapshot()
    ai_res = await ai_engine.analyze_market(snapshot, force=True)
    text = format_ai_report(ai_res)
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_ai_inline_keyboard())
    except Exception:
        pass
