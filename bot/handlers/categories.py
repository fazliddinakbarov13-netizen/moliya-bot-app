"""Category management handler."""

import re
import logging
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_menu import get_main_menu, get_settings_keyboard
from bot.utils.formatters import format_category_list
from database.repositories.user_repo import UserRepository
from database.repositories.category_repo import CategoryRepository

logger = logging.getLogger(__name__)
router = Router(name="categories")


@router.message(F.text.in_(["📂 Kategoriyalar", "📂 Категории"]))
async def categories_menu(message: Message, session: AsyncSession):
    """Show categories list."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return

    lang = user.language
    cat_repo = CategoryRepository(session)
    categories = await cat_repo.get_user_categories(message.from_user.id)

    if not categories:
        text = "Kategoriyalar topilmadi." if lang == "uz" else "Категории не найдены."
        await message.answer(text)
        return

    cat_list = format_category_list(categories, lang)
    count = len(categories)

    if lang == "ru":
        header = f"📂 <b>Ваши категории ({count}/20):</b>\n\n"
        footer = (
            "\n\n<b>Команды:</b>\n"
            "• Добавить: <i>Категория добавить: Спорт</i>\n"
            "• Удалить: <i>Категория удалить: Подарки</i>\n"
            "• Сброс: <i>Стандартные категории</i>"
        )
    else:
        header = f"📂 <b>Kategoriyalaringiz ({count}/20):</b>\n\n"
        footer = (
            "\n\n<b>Buyruqlar:</b>\n"
            "• Qo'shish: <i>Kategoriya qo'sh: Sport</i>\n"
            "• O'chirish: <i>Kategoriya o'chir: Sovg'alar</i>\n"
            "• Qaytarish: <i>Standart kategoriyalar</i>"
        )

    await message.answer(header + cat_list + footer)


# Add category via text command
@router.message(F.text.regexp(r"(?i)(kategoriya qo'sh|категория добавить)"))
async def add_category(message: Message, session: AsyncSession):
    """Add a new category."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return

    lang = user.language

    # Extract category name after colon
    match = re.search(r":\s*(.+)$", message.text)
    if not match:
        text = "⚠️ Format: <i>Kategoriya qo'sh: Sport</i>" if lang == "uz" else "⚠️ Формат: <i>Категория добавить: Спорт</i>"
        await message.answer(text)
        return

    name = match.group(1).strip()
    if not name or len(name) < 2:
        text = "⚠️ Kam 2 belgi kerak." if lang == "uz" else "⚠️ Минимум 2 символа."
        await message.answer(text)
        return

    cat_repo = CategoryRepository(session)
    try:
        result = await cat_repo.add_category(user_id=message.from_user.id, name=name)
        if result is None:
            text = "⚠️ Maksimal 20 ta kategoriya." if lang == "uz" else "⚠️ Максимум 20 категорий."
        else:
            text = f"✅ '{name}' kategoriyasi qo'shildi!" if lang == "uz" else f"✅ Категория '{name}' добавлена!"
    except Exception as e:
        logger.error(f"Error adding category: {e}")
        text = "❌ Xatolik yuz berdi." if lang == "uz" else "❌ Произошла ошибка."

    await message.answer(text, reply_markup=get_settings_keyboard(lang))


# Reset to defaults
@router.message(F.text.regexp(r"(?i)(standart kategoriyalar|стандартные категории)"))
async def reset_categories(message: Message, session: AsyncSession):
    """Reset categories to defaults."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return

    lang = user.language
    cat_repo = CategoryRepository(session)

    try:
        await cat_repo.reset_to_defaults(message.from_user.id)
        text = "✅ Standart kategoriyalar qaytarildi!" if lang == "uz" else "✅ Стандартные категории восстановлены!"
    except Exception as e:
        logger.error(f"Error resetting categories: {e}")
        text = "❌ Xatolik yuz berdi." if lang == "uz" else "❌ Произошла ошибка."

    await message.answer(text, reply_markup=get_settings_keyboard(lang))
