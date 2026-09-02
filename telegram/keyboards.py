from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
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
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

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
