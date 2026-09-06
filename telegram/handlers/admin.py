from __future__ import annotations
from datetime import datetime, timezone
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from core.config import settings
from core.logger import logger
from core.database import db_manager
from telegram.keyboards import (
    get_main_reply_keyboard,
    get_user_approval_inline_keyboard,
    get_admin_panel_inline_keyboard
)

router = Router()

async def render_admin_panel_text() -> tuple[str, int]:
    stats = await db_manager.get_user_stats()
    text = f"""👑 <b>ADMIN BOSHQARUV PANELI</b>
    
📊 <b>Foydalanuvchilar Statistikasi:</b>
• Jami ro'yxatdan o'tganlar: <b>{stats['total']}</b>
• Ruxsat berilganlar (Approved): <b>{stats['approved']}</b>
• Kutilayotgan so'rovlar (Pending): <b>{stats['pending']}</b>
• Bloklanganlar (Blocked): <b>{stats['blocked']}</b>
• 90-100% Signal Obunachilari: <b>{stats['subscribers']}</b>

📡 <b>Signal Monitor:</b> <code>Faol (24/7 scanning, har 45s)</code>
🎯 <b>Signal filtri:</b> <code>Faqat 90/100 va 100/100 A+ Setuplar</code>

⚙️ <b>Tezkor Buyruqlar:</b>
• <code>/approve &lt;ID&gt;</code> — Foydalanuvchiga ruxsat berish
• <code>/reject &lt;ID&gt;</code> — So'rovni rad etish
• <code>/block &lt;ID&gt;</code> — Bloklash
• <code>/unblock &lt;ID&gt;</code> — Blokdan chiqarish
• <code>/broadcast &lt;xabar&gt;</code> — Barchaga xabar tarqatish"""
    return text, stats['pending']

@router.message(Command("myid"))
async def cmd_myid(message: Message):
    user = await db_manager.get_user(message.chat.id)
    role = user.get("role", "USER") if user else "USER"
    status = user.get("status", "PENDING") if user else "PENDING"
    is_adm = await db_manager.is_admin(message.chat.id)

    text = f"""🆔 <b>Sizning Telegram Profil Ma'lumotlaringiz:</b>

• <b>Chat ID:</b> <code>{message.chat.id}</code>
• <b>Username:</b> @{message.from_user.username or 'Mavjud emas'}
• <b>Ism:</b> {message.from_user.first_name}
• <b>Roli:</b> <b>{'ADMIN 👑' if is_adm else role}</b>
• <b>Holati:</b> <code>{status}</code>"""
    await message.answer(text, parse_mode="HTML")

@router.message(Command("setadmin"))
async def cmd_setadmin(message: Message):
    chat_id = message.chat.id
    admins = await db_manager.get_admin_ids()

    # If already admin
    if chat_id in admins:
        await message.answer("👑 Siz allaqachon botda ADMIN hisoblanasiz!", reply_markup=get_main_reply_keyboard(is_admin=True))
        return

    # If no admins exist in system, first user can claim admin
    if len(admins) == 0 and settings.ADMIN_ID == 0:
        await db_manager.upsert_user(chat_id, message.from_user.username, message.from_user.first_name)
        await db_manager.set_user_role(chat_id, "ADMIN")
        await db_manager.set_user_status(chat_id, "APPROVED")
        await message.answer(
            "👑 <b>TABRIKLAYMIZ!</b>\n\nSiz botning <b>BOSH ADMINI</b> etib tayinlandingiz!\n"
            "Endi siz boshqa foydalanuvchilar so'rovlarini tasdiqlashingiz, bloklashingiz va butun tizimni boshqarishingiz mumkin.",
            parse_mode="HTML",
            reply_markup=get_main_reply_keyboard(is_admin=True)
        )
    else:
        await message.answer("⛔ Admin allaqachon mavjud. Faqat amaldagi admin yangi admin tayinlashi mumkin.")

@router.message(Command("admin"))
@router.message(F.text == "👑 Admin Panel")
async def cmd_admin(message: Message):
    chat_id = message.chat.id
    is_adm = await db_manager.is_admin(chat_id)

    # Check if no admin configured yet
    admins = await db_manager.get_admin_ids()
    if len(admins) == 0 and settings.ADMIN_ID == 0:
        # First person opening admin panel can become admin
        await db_manager.upsert_user(chat_id, message.from_user.username, message.from_user.first_name)
        await db_manager.set_user_role(chat_id, "ADMIN")
        await db_manager.set_user_status(chat_id, "APPROVED")
        is_adm = True

    if not is_adm:
        await message.answer("⛔ <b>Kirish taqiqlangan!</b>\nUshbu bo'lim faqat bot administratori uchun.", parse_mode="HTML")
        return

    text, pending_count = await render_admin_panel_text()
    await message.answer(text, parse_mode="HTML", reply_markup=get_admin_panel_inline_keyboard(pending_count))

@router.callback_query(F.data == "adm_refresh_panel")
async def cb_refresh_panel(call: CallbackQuery):
    if not await db_manager.is_admin(call.message.chat.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    text, pending_count = await render_admin_panel_text()
    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_panel_inline_keyboard(pending_count))
        await call.answer("Yangilandi!")
    except Exception:
        await call.answer("Ma'lumotlar o'zgarmagan.")

@router.callback_query(F.data == "adm_view_pending")
async def cb_view_pending(call: CallbackQuery):
    if not await db_manager.is_admin(call.message.chat.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    pending_users = await db_manager.get_pending_users()
    if not pending_users:
        await call.answer("Kutilayotgan so'rovlar yo'q!", show_alert=True)
        return

    await call.answer()
    for u in pending_users[:5]:
        u_id = u["chat_id"]
        u_name = u.get("first_name", "Noma'lum")
        u_user = f"@{u['username']}" if u.get("username") else "Yo'q"
        created_str = datetime.fromtimestamp(u["created_at"], timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        text = f"""📩 <b>KUTILAYOTGAN SO'ROV:</b>
👤 <b>Ismi:</b> {u_name}
🔗 <b>Username:</b> {u_user}
🆔 <b>ID:</b> <code>{u_id}</code>
📅 <b>Vaqt:</b> {created_str}"""
        await call.message.answer(text, parse_mode="HTML", reply_markup=get_user_approval_inline_keyboard(u_id))

@router.callback_query(F.data == "adm_view_users")
async def cb_view_users(call: CallbackQuery):
    if not await db_manager.is_admin(call.message.chat.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    users = await db_manager.get_all_users()
    if not users:
        await call.answer("Foydalanuvchilar mavjud emas.", show_alert=True)
        return

    await call.answer()
    lines = ["👥 <b>FOYDALANUVCHILAR RO'YXATI:</b>\n"]
    for idx, u in enumerate(users[:25], 1):
        status_icon = "✅" if u["status"] == "APPROVED" else ("⏳" if u["status"] == "PENDING" else "🚫")
        role_icon = "👑" if u["role"] == "ADMIN" else "👤"
        u_user = f"@{u['username']}" if u.get("username") else u.get("first_name", "")
        lines.append(f"{idx}. {status_icon} {role_icon} <b>{u_user}</b> (<code>{u['chat_id']}</code>) — <i>{u['status']}</i>")

    lines.append("\n<i>Amallar: /approve &lt;ID&gt; | /reject &lt;ID&gt; | /block &lt;ID&gt;</i>")
    await call.message.answer("\n".join(lines), parse_mode="HTML")

@router.callback_query(F.data == "adm_broadcast_help")
async def cb_broadcast_help(call: CallbackQuery):
    if not await db_manager.is_admin(call.message.chat.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    await call.answer()
    text = """📢 <b>XABAR TARQATISH YO'RIQNOMASI:</b>

Barcha tasdiqlangan foydalanuvchilarga xabar yuborish uchun quyidagi buyruqdan foydalaning:

<code>/broadcast Sizning xabaringiz matni</code>

<i>Misol:</i>
<code>/broadcast Diqqat! Bugun Nyu-York seansida muhim yangiliklar bor, ehtiyotkor bo'ling!</code>"""
    await call.message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "adm_monitor_status")
async def cb_monitor_status(call: CallbackQuery):
    if not await db_manager.is_admin(call.message.chat.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    subscribers = await db_manager.get_subscribers()
    text = f"""📡 <b>SIGNAL MONITOR HOLATI:</b>

• <b>Holati:</b> 🟢 Faol ishlamoqda
• <b>Tekshirish davriyligi:</b> Har 45 soniyada
• <b>Filtr mezoni:</b> Faqat 90/100 yoki 100/100 (Eng yuqori yutish ehtimoli)
• <b>Avtomatik xabar oluvchi foydalanuvchilar:</b> {len(subscribers)} ta obunachi

<i>Signal chiqqanda bot avtomat barcha tasdiqlangan foydalanuvchilarga xabar yuboradi.</i>"""
    await call.message.answer(text, parse_mode="HTML")

@router.callback_query(F.data.startswith("adm_approve_"))
async def cb_approve_user(call: CallbackQuery, bot: Bot):
    if not await db_manager.is_admin(call.message.chat.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    target_id = int(call.data.split("_")[-1])
    await db_manager.set_user_status(target_id, "APPROVED")
    user = await db_manager.get_user(target_id)
    name = user.get("first_name", "Foydalanuvchi") if user else "Foydalanuvchi"

    # Notify target user
    try:
        await bot.send_message(
            chat_id=target_id,
            text=f"🎉 <b>TABRIKLAYMIZ, {name}!</b>\n\nAdmin sizga botdan foydalanish uchun <b>ruxsat berdi</b>. Endi barcha bozor tahlillari, real-time narxlar va 90-100% avtomatik signallardan to'liq foydalanishingiz mumkin! 👇",
            parse_mode="HTML",
            reply_markup=get_main_reply_keyboard(is_admin=False)
        )
    except Exception as e:
        logger.warning(f"Foydalanuvchiga tasdiq xabarini yuborib bo'lmadi: {e}")

    await call.message.edit_text(
        f"✅ <b>Foydalanuvchi tasdiqlandi!</b>\n👤 {name} (<code>{target_id}</code>) botdan foydalanishi mumkin.",
        parse_mode="HTML"
    )
    await call.answer("Foydalanuvchiga ruxsat berildi!")

@router.callback_query(F.data.startswith("adm_reject_"))
async def cb_reject_user(call: CallbackQuery, bot: Bot):
    if not await db_manager.is_admin(call.message.chat.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    target_id = int(call.data.split("_")[-1])
    await db_manager.set_user_status(target_id, "REJECTED")

    try:
        await bot.send_message(
            chat_id=target_id,
            text="❌ <b>Kechirasiz!</b>\nAdmin sizning botdan foydalanish so'rovingizni rad etdi.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await call.message.edit_text(
        f"❌ <b>So'rov rad etildi!</b> (ID: <code>{target_id}</code>)",
        parse_mode="HTML"
    )
    await call.answer("So'rov rad etildi.")

@router.callback_query(F.data.startswith("adm_block_"))
async def cb_block_user(call: CallbackQuery, bot: Bot):
    if not await db_manager.is_admin(call.message.chat.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    target_id = int(call.data.split("_")[-1])
    await db_manager.set_user_status(target_id, "BLOCKED")

    try:
        await bot.send_message(
            chat_id=target_id,
            text="🚫 <b>Siz botda bloklandingiz.</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await call.message.edit_text(
        f"🚫 <b>Foydalanuvchi bloklandi!</b> (ID: <code>{target_id}</code>)",
        parse_mode="HTML"
    )
    await call.answer("Foydalanuvchi bloklandi.")

# Direct Commands
@router.message(Command("approve"))
async def cmd_approve_direct(message: Message, bot: Bot):
    if not await db_manager.is_admin(message.chat.id):
        return
    parts = message.text.strip().split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: <code>/approve &lt;ID&gt;</code>", parse_mode="HTML")
        return
    target_id = int(parts[1])
    await db_manager.set_user_status(target_id, "APPROVED")
    user = await db_manager.get_user(target_id)
    name = user.get("first_name", "Foydalanuvchi") if user else "Foydalanuvchi"
    try:
        await bot.send_message(
            chat_id=target_id,
            text=f"🎉 <b>TABRIKLAYMIZ!</b>\nAdmin sizga botdan foydalanish uchun ruxsat berdi!",
            parse_mode="HTML",
            reply_markup=get_main_reply_keyboard(is_admin=False)
        )
    except Exception:
        pass
    await message.answer(f"✅ {name} (<code>{target_id}</code>) tasdiqlandi.", parse_mode="HTML")

@router.message(Command("reject"))
async def cmd_reject_direct(message: Message, bot: Bot):
    if not await db_manager.is_admin(message.chat.id):
        return
    parts = message.text.strip().split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: <code>/reject &lt;ID&gt;</code>", parse_mode="HTML")
        return
    target_id = int(parts[1])
    await db_manager.set_user_status(target_id, "REJECTED")
    try:
        await bot.send_message(chat_id=target_id, text="❌ Sizning botdan foydalanish so'rovingiz rad etildi.")
    except Exception:
        pass
    await message.answer(f"❌ ID: <code>{target_id}</code> rad etildi.", parse_mode="HTML")

@router.message(Command("block"))
async def cmd_block_direct(message: Message, bot: Bot):
    if not await db_manager.is_admin(message.chat.id):
        return
    parts = message.text.strip().split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: <code>/block &lt;ID&gt;</code>", parse_mode="HTML")
        return
    target_id = int(parts[1])
    await db_manager.set_user_status(target_id, "BLOCKED")
    await message.answer(f"🚫 ID: <code>{target_id}</code> bloklandi.", parse_mode="HTML")

@router.message(Command("unblock"))
async def cmd_unblock_direct(message: Message):
    if not await db_manager.is_admin(message.chat.id):
        return
    parts = message.text.strip().split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: <code>/unblock &lt;ID&gt;</code>", parse_mode="HTML")
        return
    target_id = int(parts[1])
    await db_manager.set_user_status(target_id, "APPROVED")
    await message.answer(f"✅ ID: <code>{target_id}</code> blokdan chiqarildi va tasdiqlandi.", parse_mode="HTML")

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot):
    if not await db_manager.is_admin(message.chat.id):
        return

    text_to_send = message.text.replace("/broadcast", "", 1).strip()
    if not text_to_send:
        await message.answer("Foydalanish: <code>/broadcast Sizning xabaringiz</code>", parse_mode="HTML")
        return

    subscribers = await db_manager.get_subscribers()
    if not subscribers:
        await message.answer("Obunachilar topilmadi.")
        return

    sent_count = 0
    fail_count = 0
    msg = await message.answer(f"⏳ {len(subscribers)} ta foydalanuvchiga xabar yuborilmoqda...")

    for chat_id in subscribers:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f"📢 <b>ADMIN XABARI:</b>\n\n{text_to_send}",
                parse_mode="HTML"
            )
            sent_count += 1
        except Exception:
            fail_count += 1

    await msg.edit_text(
        f"✅ <b>Xabar tarqatildi!</b>\n\n• Muvaffaqiyatli yetkazildi: <b>{sent_count}</b> ta\n• Yetkazilmadi: <b>{fail_count}</b> ta",
        parse_mode="HTML"
    )
