"""Inline keyboards for confirmations and selections."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_expense_confirm_keyboard(
    items: list[dict], lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Confirmation keyboard after AI categorization.

    items: [{"category": "Oziq-ovqat", "category_id": 1, "amount": 45000, "icon": "🍞"}]
    """
    builder = InlineKeyboardBuilder()

    confirm_text = "✅ Tasdiqlash" if lang == "uz" else "✅ Подтвердить"
    edit_text = "✏️ Tahrirlash" if lang == "uz" else "✏️ Изменить"
    cancel_text = "❌ Bekor qilish" if lang == "uz" else "❌ Отмена"

    builder.row(
        InlineKeyboardButton(text=confirm_text, callback_data="expense_confirm"),
        InlineKeyboardButton(text=edit_text, callback_data="expense_edit"),
    )
    builder.row(
        InlineKeyboardButton(text=cancel_text, callback_data="expense_cancel"),
    )
    return builder.as_markup()


def get_category_select_keyboard(
    categories: list, lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Build category selection inline keyboard."""
    builder = InlineKeyboardBuilder()

    for cat in categories:
        name = cat.name_uz if lang == "uz" else cat.name_ru
        builder.button(
            text=f"{cat.icon} {name}",
            callback_data=f"cat_select:{cat.id}",
        )

    # 2 buttons per row
    builder.adjust(2)

    # Add cancel button
    cancel_text = "❌ Bekor qilish" if lang == "uz" else "❌ Отмена"
    builder.row(InlineKeyboardButton(text=cancel_text, callback_data="cat_cancel"))

    return builder.as_markup()


def get_wallet_select_keyboard(
    wallets: list, lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Build wallet selection inline keyboard."""
    builder = InlineKeyboardBuilder()

    for wallet in wallets:
        builder.button(
            text=f"{wallet.icon} {wallet.name}",
            callback_data=f"wallet_select:{wallet.id}",
        )

    builder.adjust(2)
    return builder.as_markup()


def get_month_select_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Month selection for reports."""
    from bot.utils.constants import MONTH_NAMES_UZ, MONTH_NAMES_RU

    months = MONTH_NAMES_UZ if lang == "uz" else MONTH_NAMES_RU
    builder = InlineKeyboardBuilder()

    for num, name in months.items():
        builder.button(text=name, callback_data=f"month_select:{num}")

    builder.adjust(3)
    return builder.as_markup()


def get_report_type_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Report type selection."""
    builder = InlineKeyboardBuilder()

    if lang == "ru":
        builder.button(text="📊 Текущий месяц", callback_data="report_current")
        builder.button(text="📅 Выбрать месяц", callback_data="report_select_month")
        builder.button(text="📈 Сравнение", callback_data="report_compare")
        builder.button(text="📋 Годовой", callback_data="report_yearly")
    else:
        builder.button(text="📊 Joriy oy", callback_data="report_current")
        builder.button(text="📅 Oyni tanlash", callback_data="report_select_month")
        builder.button(text="📈 Taqqoslash", callback_data="report_compare")
        builder.button(text="📋 Yillik", callback_data="report_yearly")

    builder.adjust(2)
    return builder.as_markup()


def get_category_action_keyboard(
    category_id: int, lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Category management actions."""
    builder = InlineKeyboardBuilder()

    if lang == "ru":
        builder.button(text="✏️ Переименовать", callback_data=f"cat_rename:{category_id}")
        builder.button(text="🎨 Иконка", callback_data=f"cat_icon:{category_id}")
        builder.button(text="🗑 Удалить", callback_data=f"cat_delete:{category_id}")
    else:
        builder.button(text="✏️ Nomini o'zgartirish", callback_data=f"cat_rename:{category_id}")
        builder.button(text="🎨 Ikonka", callback_data=f"cat_icon:{category_id}")
        builder.button(text="🗑 O'chirish", callback_data=f"cat_delete:{category_id}")

    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga" if lang == "uz" else "🔙 Назад",
            callback_data="cat_back",
        )
    )
    return builder.as_markup()


def get_delete_confirm_keyboard(
    item_id: int, item_type: str, lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Delete confirmation keyboard."""
    builder = InlineKeyboardBuilder()

    if lang == "ru":
        builder.button(text="✅ Да, удалить", callback_data=f"confirm_delete:{item_type}:{item_id}")
        builder.button(text="❌ Нет", callback_data="cancel_delete")
    else:
        builder.button(text="✅ Ha, o'chirish", callback_data=f"confirm_delete:{item_type}:{item_id}")
        builder.button(text="❌ Yo'q", callback_data="cancel_delete")

    builder.adjust(2)
    return builder.as_markup()
