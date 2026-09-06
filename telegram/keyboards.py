from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_reply_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Persistent bottom keyboard for 1-tap navigation."""
    kb = [
        [
            KeyboardButton(text="🎯 Savdo Sxemasi"),
            KeyboardButton(text="📊 Dashboard")
        ],
        [
            KeyboardButton(text="🟡 Oltin Narxi"),
            KeyboardButton(text="📈 Texnik Tahlil"),
            KeyboardButton(text="🌐 Makro Tahlil")
        ],
        [
            KeyboardButton(text="🤖 AI Analiz"),
            KeyboardButton(text="📝 Paper Trade"),
            KeyboardButton(text="🩺 Tizim Holati")
        ]
    ]
    if is_admin:
        kb.append([KeyboardButton(text="👑 Admin Panel")])

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_pending_reply_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for users waiting for admin approval."""
    kb = [
        [
            KeyboardButton(text="🔄 Ruxsat holatini tekshirish"),
            KeyboardButton(text="📩 Adminga so'rov yuborish")
        ],
        [
            KeyboardButton(text="ℹ️ Bot haqida ma'lumot")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_user_approval_inline_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """Inline buttons sent to admin when a new user registers."""
    kb = [
        [
            InlineKeyboardButton(text="✅ Ruxsat berish", callback_data=f"adm_approve_{chat_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"adm_reject_{chat_id}")
        ],
        [
            InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"adm_block_{chat_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_admin_panel_inline_keyboard(pending_count: int = 0) -> InlineKeyboardMarkup:
    """Inline dashboard for Admin Panel."""
    kb = [
        [
            InlineKeyboardButton(text=f"⏳ So'rovlar ({pending_count})", callback_data="adm_view_pending"),
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="adm_view_users")
        ],
        [
            InlineKeyboardButton(text="📢 Xabar tarqatish", callback_data="adm_broadcast_help"),
            InlineKeyboardButton(text="📡 Signal Monitor", callback_data="adm_monitor_status")
        ],
        [
            InlineKeyboardButton(text="📊 To'liq Statistika", callback_data="adm_stats"),
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="adm_refresh_panel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_dashboard_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline quick action buttons under Dashboard."""
    kb = [
        [
            InlineKeyboardButton(text="🎯 Savdo Sxemasi Ol", callback_data="act_scheme"),
            InlineKeyboardButton(text="🤖 AI Analiz Ol", callback_data="act_ai")
        ],
        [
            InlineKeyboardButton(text="🟢 Paper BUY", callback_data="act_buy"),
            InlineKeyboardButton(text="🔴 Paper SELL", callback_data="act_sell")
        ],
        [
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="act_refresh_dash")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_ai_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline buttons under AI analysis."""
    kb = [
        [
            InlineKeyboardButton(text="🎯 Reja/Sxema Tuzish", callback_data="act_scheme"),
            InlineKeyboardButton(text="📈 Texnik Tafsilot", callback_data="act_tech")
        ],
        [
            InlineKeyboardButton(text="🔄 Analizni Yangilash", callback_data="act_ai_force")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
