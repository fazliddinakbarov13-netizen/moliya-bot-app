"""Main menu and reply keyboards."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, WebAppInfo

# Telegram faqat HTTPS manzillarni qabul qiladi. Lokal test uchun istalgan xavfsiz URL qo'yib turamiz.
LOCAL_WEB_APP_URL = "https://moliyabot-demo.netlify.app" # Deploy bo'lguncha turg'un dummy havolasi

def get_main_menu(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    if lang == "ru":
        buttons = [
            [KeyboardButton(text="📱 Открыть приложение", web_app=WebAppInfo(url=LOCAL_WEB_APP_URL))],
            [KeyboardButton(text="📝 Расход"), KeyboardButton(text="💰 Доход")],
            [KeyboardButton(text="📊 Отчёт"), KeyboardButton(text="🎯 Цели")],
            [KeyboardButton(text="💳 Кредиты"), KeyboardButton(text="👛 Счета")],
            [KeyboardButton(text="🤝 Долги"), KeyboardButton(text="⚙️ Настройки")],
        ]
    else:
        buttons = [
            [KeyboardButton(text="📱 Ilovani ochish", web_app=WebAppInfo(url=LOCAL_WEB_APP_URL))],
            [KeyboardButton(text="📝 Xarajat"), KeyboardButton(text="💰 Daromad")],
            [KeyboardButton(text="📊 Hisobot"), KeyboardButton(text="🎯 Maqsadlar")],
            [KeyboardButton(text="💳 Kreditlar"), KeyboardButton(text="👛 Hisoblarim")],
            [KeyboardButton(text="🤝 Qarzlarim"), KeyboardButton(text="⚙️ Sozlamalar")],
        ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        is_persistent=True,
    )


def get_language_keyboard() -> ReplyKeyboardMarkup:
    """Language selection keyboard."""
    buttons = [
        [KeyboardButton(text="🇺🇿 O'zbek tili")],
        [KeyboardButton(text="🇷🇺 Русский язык")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def get_family_status_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Family status selection keyboard."""
    if lang == "ru":
        buttons = [
            [KeyboardButton(text="👤 Один/Одна")],
            [KeyboardButton(text="👫 Семейный")],
        ]
    else:
        buttons = [
            [KeyboardButton(text="👤 Yolg'iz")],
            [KeyboardButton(text="👫 Oilaviy")],
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def get_currency_keyboard() -> ReplyKeyboardMarkup:
    """Currency selection keyboard."""
    buttons = [
        [KeyboardButton(text="🇺🇿 So'm (UZS)")],
        [KeyboardButton(text="🇺🇸 Dollar (USD)")],
        [KeyboardButton(text="🇪🇺 Yevro (EUR)")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def get_skip_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Skip button keyboard."""
    text = "⏭ O'tkazib yuborish" if lang == "uz" else "⏭ Пропустить"
    buttons = [[KeyboardButton(text=text)]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def get_cancel_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Cancel button keyboard."""
    text = "❌ Bekor qilish" if lang == "uz" else "❌ Отмена"
    buttons = [[KeyboardButton(text=text)]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def get_confirm_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Yes/No confirmation keyboard."""
    if lang == "ru":
        buttons = [
            [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")],
        ]
    else:
        buttons = [
            [KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo'q")],
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def get_settings_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Settings menu keyboard."""
    if lang == "ru":
        buttons = [
            [KeyboardButton(text="🌐 Язык"), KeyboardButton(text="💱 Валюта")],
            [KeyboardButton(text="📂 Категории"), KeyboardButton(text="🔔 Напоминание")],
            [KeyboardButton(text="🔄 Повторяющиеся"), KeyboardButton(text="👨‍👩‍👧 Семья")],
            [KeyboardButton(text="🔙 Назад")],
        ]
    else:
        buttons = [
            [KeyboardButton(text="🌐 Til"), KeyboardButton(text="💱 Valyuta")],
            [KeyboardButton(text="📂 Kategoriyalar"), KeyboardButton(text="🔔 Eslatma")],
            [KeyboardButton(text="🔄 Takroriy"), KeyboardButton(text="👨‍👩‍👧 Oila")],
            [KeyboardButton(text="🔙 Orqaga")],
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, is_persistent=True)


def get_income_type_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Income type selection keyboard."""
    if lang == "ru":
        buttons = [
            [KeyboardButton(text="💼 Зарплата")],
            [KeyboardButton(text="💼 Зарплата (2-й)")],
            [KeyboardButton(text="📈 Доп. доход")],
            [KeyboardButton(text="💵 Прочий доход")],
            [KeyboardButton(text="❌ Отмена")],
        ]
    else:
        buttons = [
            [KeyboardButton(text="💼 Oylik maosh")],
            [KeyboardButton(text="💼 Ikkinchi kishi oyligi")],
            [KeyboardButton(text="📈 Qo'shimcha daromad")],
            [KeyboardButton(text="💵 Boshqa daromad")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def remove_keyboard() -> ReplyKeyboardRemove:
    """Remove reply keyboard."""
    return ReplyKeyboardRemove()
