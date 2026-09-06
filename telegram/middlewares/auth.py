from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from core.database import db_manager
from telegram.keyboards import get_pending_reply_keyboard

class AuthMiddleware(BaseMiddleware):
    """
    Guards all bot handlers.
    Only allows APPROVED users and ADMINS to access market intelligence,
    signals, AI analysis, and trading features.
    """
    async def __call__(self, handler, event, data):
        user_id = None

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            text = event.text or ""

            # Unrestricted commands & actions
            if text.startswith(("/start", "/help", "/myid", "/setadmin")) or text in [
                "🔄 Ruxsat holatini tekshirish",
                "📩 Adminga so'rov yuborish",
                "ℹ️ Bot haqida ma'lumot"
            ]:
                return await handler(event, data)

        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
            # Admin-specific callbacks have their own admin verification
            if event.data and event.data.startswith("adm_"):
                return await handler(event, data)

        if not user_id:
            return await handler(event, data)

        # Check user in DB
        user = await db_manager.get_user(user_id)
        if not user:
            user = await db_manager.upsert_user(
                user_id,
                event.from_user.username,
                event.from_user.first_name
            )

        role = user.get("role", "USER")
        status = user.get("status", "PENDING")

        # Allow Admins and Approved users
        if role == "ADMIN" or status == "APPROVED":
            return await handler(event, data)

        # Blocked users
        if status == "BLOCKED":
            if isinstance(event, Message):
                await event.answer("🚫 <b>Kechirasiz, siz ushbu botda bloklangansiz.</b>", parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.answer("Siz bloklangansiz!", show_alert=True)
            return

        # Pending or Rejected users
        if isinstance(event, Message):
            await event.answer(
                "🔒 <b>Botdan foydalanish uchun Admin ruxsati zarur!</b>\n\n"
                "Sizning so'rovingiz adminga yuborilgan. Admin tasdiqlashi bilan barcha imkoniyatlar avtomatik tarzda ochiladi.",
                parse_mode="HTML",
                reply_markup=get_pending_reply_keyboard()
            )
        elif isinstance(event, CallbackQuery):
            await event.answer("Admin ruxsati kutilmoqda!", show_alert=True)
        return
