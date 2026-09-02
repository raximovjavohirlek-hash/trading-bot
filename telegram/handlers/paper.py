from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from analytics.snapshot_engine import snapshot_engine
from trading.paper_engine import paper_engine
from trading.risk_engine import risk_engine
from core.database import db_manager
from telegram.keyboards import get_main_reply_keyboard

router = Router()

@router.message(Command("paper"))
@router.message(F.text == "📝 Paper Trade")
async def cmd_paper(message: Message):
    open_trades = await db_manager.get_open_paper_trades()
    snapshot = await snapshot_engine.generate_snapshot()
    price = snapshot["price"]

    text = f"""📝 <b>PAPER TRADING (VIRTUAL SAVDO SIMULYATSIYASI)</b>

Hozirgi Oltin narxi: <b>${price:.2f}</b>
Ochiq pozitsiyalar soni: <b>{len(open_trades)}</b>

Savdo sinovini boshlash uchun <code>/paper BUY</code> yoki <code>/paper SELL</code> yozing yoki inline tugmalardan foydalaning."""
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())

@router.message(Command("trades"))
async def cmd_trades(message: Message):
    open_trades = await db_manager.get_open_paper_trades()
    if not open_trades:
        await message.answer("ℹ️ Hozirda ochiq paper trade pozitsiyalari mavjud emas.", reply_markup=get_main_reply_keyboard())
        return

    lines = []
    for t in open_trades:
        lines.append(f"• #{t['id']} <b>{t['type']}</b> @ ${t['entry_price']:.2f} (SL: ${t['sl']:.2f}, TP: ${t['tp']:.2f})")
    
    text = "📋 <b>OCHIQ PAPER TRADE POZITSIYALARI:</b>\n\n" + "\n".join(lines)
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())

@router.callback_query(F.data.in_({"act_buy", "act_sell"}))
async def cb_paper_trade(call: CallbackQuery):
    await call.answer()
    trade_type = "BUY" if call.data == "act_buy" else "SELL"
    snapshot = await snapshot_engine.generate_snapshot()
    entry = snapshot["price"]
    atr = snapshot.get("tech_m15", {}).get("atr", 3.5)

    if trade_type == "BUY":
        sl = round(entry - (atr * 2.0), 2)
        tp = round(entry + (atr * 3.5), 2)
    else:
        sl = round(entry + (atr * 2.0), 2)
        tp = round(entry - (atr * 3.5), 2)

    res = await paper_engine.open_trade("XAUUSD", trade_type, entry, sl, tp)
    lot_calc = risk_engine.calculate_lot_size(10000.0, 1.0, entry, sl)

    text = f"""📝 <b>PAPER TRADE OCHILDI (#{res['trade_id']})</b>

• Tur: <b>{trade_type}</b>
• Kirish Narxi: <b>${entry:.2f}</b>
• Stop Loss (SL): <b>${sl:.2f}</b>
• Take Profit (TP): <b>${tp:.2f}</b>
• Tavsiya qilingan Lot ($10k balans, 1% risk): <b>{lot_calc['lots']} Lot</b>

<i>Virtual pozitsiya bo'yicha TP/SL natijalari avtomatik kuzatiladi.</i>"""
    await call.message.answer(text, parse_mode="HTML")
