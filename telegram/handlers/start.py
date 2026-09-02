from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from telegram.keyboards import get_main_reply_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Assalomu alaykum! 🟡\n\n"
        "<b>XAUUSD Real-Time Market Intelligence & AI Platform</b>ga xush kelibsiz.\n\n"
        "Barcha buyruqlar va tahlillar pastdagi <b>qulay tugmalarda (menyuda)</b> joylashtirildi. Shunchaki keragini bosing! 👇",
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_start(message)
