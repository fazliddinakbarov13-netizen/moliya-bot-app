"""Constants and default values for the bot."""

# Default 15 expense categories
DEFAULT_CATEGORIES = [
    {"name": "Oziq-ovqat", "name_uz": "Oziq-ovqat", "name_ru": "Продукты", "icon": "🍞"},
    {"name": "Uy xarajatlari", "name_uz": "Uy xarajatlari", "name_ru": "Домашние расходы", "icon": "🏠"},
    {"name": "Kommunal to'lovlar", "name_uz": "Kommunal to'lovlar", "name_ru": "Коммунальные", "icon": "💡"},
    {"name": "Kiyim-kechak", "name_uz": "Kiyim-kechak", "name_ru": "Одежда", "icon": "👔"},
    {"name": "Sog'liq", "name_uz": "Sog'liq", "name_ru": "Здоровье", "icon": "💊"},
    {"name": "Gigiena", "name_uz": "Gigiena", "name_ru": "Гигиена", "icon": "🧴"},
    {"name": "Aloqa", "name_uz": "Aloqa", "name_ru": "Связь", "icon": "📱"},
    {"name": "Transport", "name_uz": "Transport", "name_ru": "Транспорт", "icon": "🚕"},
    {"name": "Ta'lim", "name_uz": "Ta'lim", "name_ru": "Образование", "icon": "📚"},
    {"name": "Farzandlar", "name_uz": "Farzandlar", "name_ru": "Дети", "icon": "👶"},
    {"name": "Ko'ngil ochar", "name_uz": "Ko'ngil ochar", "name_ru": "Развлечения", "icon": "🎬"},
    {"name": "Sovg'alar", "name_uz": "Sovg'alar", "name_ru": "Подарки", "icon": "🎁"},
    {"name": "Ehson", "name_uz": "Ehson", "name_ru": "Пожертвования", "icon": "🤲"},
    {"name": "Kutilmagan xarajatlar", "name_uz": "Kutilmagan xarajatlar", "name_ru": "Непредвиденные", "icon": "⚡"},
    {"name": "Choyxona/Kafe", "name_uz": "Choyxona/Kafe", "name_ru": "Чайхана/Кафе", "icon": "☕"},
]

# Income types
INCOME_TYPES = {
    "salary": {"uz": "Oylik maosh", "ru": "Зарплата"},
    "salary_2": {"uz": "Ikkinchi kishi oyligi", "ru": "Зарплата (2-й)"},
    "additional": {"uz": "Qo'shimcha daromad", "ru": "Доп. доход"},
    "other": {"uz": "Boshqa daromad", "ru": "Прочий доход"},
}

# Currency symbols
CURRENCY_SYMBOLS = {
    "UZS": "so'm",
    "USD": "$",
    "EUR": "€",
}

# Month names
MONTH_NAMES_UZ = {
    1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
    5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
    9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr",
}

MONTH_NAMES_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}

# Wallet types
DEFAULT_WALLETS = [
    {"name": "Naqd pul", "type": "cash", "icon": "💵"},
    {"name": "Uzcard", "type": "card", "icon": "💳"},
    {"name": "Humo", "type": "card", "icon": "💳"},
    {"name": "Visa", "type": "card", "icon": "💎"},
]

# Budget warning threshold
BUDGET_WARNING_PERCENT = 80

# Progress bar characters
PROGRESS_FULL = "█"
PROGRESS_EMPTY = "░"
PROGRESS_LENGTH = 15

# Onboarding steps
FAMILY_STATUSES = {
    "single": {"uz": "Yolg'iz", "ru": "Один/Одна"},
    "family": {"uz": "Oilaviy", "ru": "Семейный"},
}

CURRENCIES = {
    "UZS": {"uz": "🇺🇿 So'm (UZS)", "ru": "🇺🇿 Сум (UZS)"},
    "USD": {"uz": "🇺🇸 Dollar (USD)", "ru": "🇺🇸 Доллар (USD)"},
    "EUR": {"uz": "🇪🇺 Yevro (EUR)", "ru": "🇪🇺 Евро (EUR)"},
}

LANGUAGES = {
    "uz": "🇺🇿 O'zbek tili",
    "ru": "🇷🇺 Русский язык",
    "en": "🇬🇧 English",
}
