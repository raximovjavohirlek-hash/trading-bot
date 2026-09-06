from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from core.database import db_manager
from telegram.keyboards import get_main_reply_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await db_manager.add_subscriber(
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    await message.answer(
        "Assalomu alaykum! 🟡\n\n"
        "<b>XAUUSD Real-Time Market Intelligence & AI Platform</b>ga xush kelibsiz.\n\n"
        "Siz 90-100% yuqori ehtimollikdagi (High-Probability A+) savdo signallari uchun <b>avtomatik xabarnoma tizimi</b>ga ulandingiz! 🔔\n\n"
        "Barcha buyruqlar va tahlillar pastdagi <b>qulay tugmalarda (menyuda)</b> joylashtirildi. Shunchaki keragini bosing! 👇",
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_start(message)
