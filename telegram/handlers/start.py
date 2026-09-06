from datetime import datetime, timezone
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from core.database import db_manager
from telegram.keyboards import (
    get_main_reply_keyboard,
    get_pending_reply_keyboard,
    get_user_approval_inline_keyboard
)

router = Router()

async def notify_admins_of_pending_user(bot: Bot, user: dict):
    admin_ids = await db_manager.get_admin_ids()
    if not admin_ids:
        return

    name = user.get("first_name", "Noma'lum")
    u_name = f"@{user['username']}" if user.get("username") else "Yo'q"
    chat_id = user["chat_id"]
    time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    text = f"""🔔 <b>YANGI FOYDALANUVCHI RO'YXATDAN O'TMOQCHI!</b>

👤 <b>Ismi:</b> {name}
🔗 <b>Username:</b> {u_name}
🆔 <b>Chat ID:</b> <code>{chat_id}</code>
📅 <b>Vaqt:</b> {time_str}

Ushbu foydalanuvchiga botdan foydalanish uchun ruxsat berasizmi?"""

    for adm_id in admin_ids:
        try:
            await bot.send_message(
                chat_id=adm_id,
                text=text,
                parse_mode="HTML",
                reply_markup=get_user_approval_inline_keyboard(chat_id)
            )
        except Exception:
            pass

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = await db_manager.upsert_user(
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    role = user.get("role", "USER")
    status = user.get("status", "PENDING")

    # 1. ADMIN USER
    if role == "ADMIN":
        await message.answer(
            f"Assalomu alaykum, Xo'jayin (Admin) <b>{message.from_user.first_name}</b>! 👑\n\n"
            f"Siz botning to'laqonli egasisiz. Barcha tizimlar, signallar va foydalanuvchilar sizning nazoratingizda.\n\n"
            f"Boshqaruv uchun pastdagi <b>👑 Admin Panel</b> tugmasidan foydalaning yoki /admin buyrug'ini yuboring! 👇",
            parse_mode="HTML",
            reply_markup=get_main_reply_keyboard(is_admin=True)
        )
        return

    # 2. BLOCKED USER
    if status == "BLOCKED":
        await message.answer("🚫 <b>Kechirasiz, siz ushbu botda bloklangansiz.</b>", parse_mode="HTML")
        return

    # 3. APPROVED USER
    if status == "APPROVED":
        await message.answer(
            f"Assalomu alaykum, <b>{message.from_user.first_name}</b>! 🟡\n\n"
            f"<b>XAUUSD Real-Time Institutional Trading & AI Platform</b>ga xush kelibsiz.\n\n"
            f"Sizning hisobingiz admin tomonidan tasdiqlangan. Siz 90-100% yuqori ehtimollikdagi A+ signallarni avtomatik qabul qilasiz! 🔔\n\n"
            f"Kerakli bo'limni pastdagi menyudan tanlang! 👇",
            parse_mode="HTML",
            reply_markup=get_main_reply_keyboard(is_admin=False)
        )
        return

    # 4. PENDING USER (Waiting for admin approval)
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>! 🟡\n\n"
        f"🔒 <b>Ushbu bot xususiy (yopiq) professional savdo tizimi hisoblanadi.</b>\n"
        f"Botdan foydalanish uchun <b>Admin ruxsati</b> talab qilinadi.\n\n"
        f"📩 <i>Sizning so'rovingiz adminga yuborildi! Admin tasdiqlashi bilan sizga avtomatik tarzda xabar keladi va bot menyusi ochiladi.</i>",
        parse_mode="HTML",
        reply_markup=get_pending_reply_keyboard()
    )

    # Send notification to Admin with Approve/Reject buttons
    await notify_admins_of_pending_user(bot, user)

@router.message(F.text == "🔄 Ruxsat holatini tekshirish")
async def check_status(message: Message):
    user = await db_manager.get_user(message.chat.id)
    if not user:
        await cmd_start(message)
        return

    role = user.get("role", "USER")
    status = user.get("status", "PENDING")

    if role == "ADMIN":
        await message.answer("👑 Siz bot adminsiz!", reply_markup=get_main_reply_keyboard(is_admin=True))
    elif status == "APPROVED":
        await message.answer("🎉 <b>Ruxsat berilgan!</b> Botdan to'liq foydalanishingiz mumkin.", parse_mode="HTML", reply_markup=get_main_reply_keyboard(is_admin=False))
    elif status == "BLOCKED":
        await message.answer("🚫 Siz bloklangansiz.")
    else:
        await message.answer("⏳ <b>Ruxsat kutilmoqda...</b>\nAdmin hali so'rovingizni ko'rib chiqmoqda. Iltimos, kuting.", parse_mode="HTML")

@router.message(F.text == "📩 Adminga so'rov yuborish")
async def resend_request(message: Message, bot: Bot):
    user = await db_manager.get_user(message.chat.id)
    if not user:
        user = await db_manager.upsert_user(message.chat.id, message.from_user.username, message.from_user.first_name)

    if user.get("status") == "APPROVED":
        await message.answer("Sizga allaqachon ruxsat berilgan!", reply_markup=get_main_reply_keyboard(is_admin=(user.get("role") == "ADMIN")))
        return

    await notify_admins_of_pending_user(bot, user)
    await message.answer("✅ <i>Adminga qayta so'rov va eslatma yuborildi!</i>", parse_mode="HTML")

@router.message(F.text == "ℹ️ Bot haqida ma'lumot")
async def bot_info(message: Message):
    await message.answer(
        "🤖 <b>XAUUSD Real-Time Institutional Trading Bot</b>\n\n"
        "• Faqat 100% faktik real bozor raqamlari (TradingView OANDA spot, Real DXY, Real US10Y).\n"
        "• Smart Money Concepts (SMC) va Candle Range Theory (CRT) strategiyasi.\n"
        "• Faqat 90/100 yoki 100/100 yuqori yutish ehtimoli bo'lganda avtomat xabar yuborish.\n"
        "• Yopiq tizim — faqat Admin ruxsati bilan ishlaydi.",
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def cmd_help(message: Message, bot: Bot):
    await cmd_start(message, bot)
