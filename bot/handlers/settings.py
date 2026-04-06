"""Settings handler.

NOTE: Language/currency handlers here only work for ONBOARDED users.
During onboarding, the start.py handlers take priority via FSM states.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_menu import (
    get_main_menu,
    get_settings_keyboard,
    get_language_keyboard,
    get_currency_keyboard,
)
from database.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)
router = Router(name="settings")


@router.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки"]))
async def settings_menu(message: Message, state: FSMContext, session: AsyncSession):
    """Show settings menu."""
    # Clear any lingering state
    await state.clear()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return

    lang = user.language
    text = "⚙️ <b>Sozlamalar:</b>" if lang == "uz" else "⚙️ <b>Настройки:</b>"
    await message.answer(text, reply_markup=get_settings_keyboard(lang))


@router.message(F.text.in_(["🔙 Orqaga", "🔙 Назад"]))
async def back_to_main(message: Message, state: FSMContext, session: AsyncSession):
    """Go back to main menu."""
    await state.clear()
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user else "uz"
    await message.answer("🏠", reply_markup=get_main_menu(lang))


@router.message(F.text.in_(["🌐 Til", "🌐 Язык"]))
async def change_language(message: Message, session: AsyncSession):
    """Change language."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return
    await message.answer("🌐 Tilni tanlang / Выберите язык:", reply_markup=get_language_keyboard())


@router.message(F.text.in_(["💱 Valyuta", "💱 Валюта"]))
async def change_currency(message: Message, session: AsyncSession):
    """Change currency."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return
    await message.answer("💱 Valyutani tanlang:", reply_markup=get_currency_keyboard())


# Handle language change from settings
# Using exact button text match to avoid conflicts
@router.message(F.text == "🇺🇿 O'zbek tili")
@router.message(F.text == "🇷🇺 Русский язык")
async def process_language_change(message: Message, state: FSMContext, session: AsyncSession):
    """Process language change from settings (only for onboarded users)."""
    # Skip if in any FSM state (e.g., onboarding) — let the state handler process it
    current_state = await state.get_state()
    if current_state is not None:
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return

    new_lang = "uz" if "O'zbek" in message.text else "ru"
    await user_repo.update_user(message.from_user.id, language=new_lang)

    if new_lang == "ru":
        text = "✅ Язык изменён на русский."
    else:
        text = "✅ Til o'zbek tiliga o'zgartirildi."

    await message.answer(text, reply_markup=get_main_menu(new_lang))


# Handle currency change from settings
@router.message(F.text.in_(["🇺🇿 So'm (UZS)", "🇺🇸 Dollar (USD)", "🇪🇺 Yevro (EUR)"]))
async def process_currency_change(message: Message, state: FSMContext, session: AsyncSession):
    """Process currency change (only for onboarded users, not in FSM state)."""
    current_state = await state.get_state()
    if current_state is not None:
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return

    if "UZS" in message.text:
        new_currency = "UZS"
    elif "USD" in message.text:
        new_currency = "USD"
    elif "EUR" in message.text:
        new_currency = "EUR"
    else:
        return

    await user_repo.update_user(message.from_user.id, currency=new_currency)

    lang = user.language
    text = f"✅ Valyuta {new_currency} ga o'zgartirildi." if lang == "uz" else f"✅ Валюта изменена на {new_currency}."
    await message.answer(text, reply_markup=get_settings_keyboard(lang))


@router.message(F.text.in_(["🔔 Eslatma", "🔔 Напоминание"]))
async def toggle_reminder(message: Message, session: AsyncSession):
    """Toggle daily reminder."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return

    lang = user.language
    new_state = not user.reminder_enabled
    await user_repo.update_user(message.from_user.id, reminder_enabled=new_state)

    if new_state:
        text = f"🔔 Kundalik eslatma yoqildi (soat {user.reminder_hour}:00)" if lang == "uz" else f"🔔 Напоминание включено ({user.reminder_hour}:00)"
    else:
        text = "🔕 Kundalik eslatma o'chirildi." if lang == "uz" else "🔕 Напоминание отключено."

    await message.answer(text, reply_markup=get_settings_keyboard(lang))


# ── Handle unhandled menu buttons ───────────────────────────────────
@router.message(F.text.in_(["🎯 Maqsadlar", "🎯 Цели"]))
async def goals_placeholder(message: Message, session: AsyncSession):
    """Goals placeholder."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user else "uz"
    text = "🎯 Maqsadlar bo'limi tez orada qo'shiladi!" if lang == "uz" else "🎯 Раздел целей будет добавлен в ближайшее время!"
    await message.answer(text, reply_markup=get_main_menu(lang))


@router.message(F.text.in_(["💳 Kreditlar", "💳 Кредиты"]))
async def credits_placeholder(message: Message, session: AsyncSession):
    """Credits placeholder."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user else "uz"
    text = "💳 Kreditlar bo'limi tez orada qo'shiladi!" if lang == "uz" else "💳 Раздел кредитов будет добавлен в ближайшее время!"
    await message.answer(text, reply_markup=get_main_menu(lang))


@router.message(F.text.in_(["👛 Hisoblarim", "👛 Счета"]))
async def wallets_placeholder(message: Message, session: AsyncSession):
    """Wallets placeholder."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user else "uz"

    from database.repositories.wallet_repo import WalletRepository
    wallet_repo = WalletRepository(session)
    wallets = await wallet_repo.get_user_wallets(message.from_user.id)

    if wallets:
        from bot.utils.formatters import format_money
        currency = user.currency if user else "UZS"
        lines = [f"👛 <b>{'Hisoblaringiz' if lang == 'uz' else 'Ваши счета'}:</b>\n"]
        for w in wallets:
            lines.append(f"  {w.icon} {w.name}: <b>{format_money(w.balance, currency)}</b>")
        await message.answer("\n".join(lines), reply_markup=get_main_menu(lang))
    else:
        text = "👛 Hisoblar topilmadi." if lang == "uz" else "👛 Счета не найдены."
        await message.answer(text, reply_markup=get_main_menu(lang))


@router.message(F.text.in_(["🤝 Qarzlarim", "🤝 Долги"]))
async def debts_placeholder(message: Message, session: AsyncSession):
    """Debts placeholder."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user else "uz"
    text = "🤝 Qarzlar bo'limi tez orada qo'shiladi!" if lang == "uz" else "🤝 Раздел долгов будет добавлен в ближайшее время!"
    await message.answer(text, reply_markup=get_main_menu(lang))


@router.message(F.text.in_(["🔄 Takroriy", "🔄 Повторяющиеся"]))
async def recurring_placeholder(message: Message, session: AsyncSession):
    """Recurring placeholder."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user else "uz"
    text = "🔄 Takroriy xarajatlar tez orada qo'shiladi!" if lang == "uz" else "🔄 Повторяющиеся расходы будут добавлены позже!"
    await message.answer(text, reply_markup=get_settings_keyboard(lang))


@router.message(F.text.in_(["👨‍👩‍👧 Oila", "👨‍👩‍👧 Семья"]))
async def family_placeholder(message: Message, session: AsyncSession):
    """Family placeholder."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user else "uz"
    text = "👨‍👩‍👧 Oila bo'limi tez orada qo'shiladi!" if lang == "uz" else "👨‍👩‍👧 Семейный раздел будет добавлен позже!"
    await message.answer(text, reply_markup=get_settings_keyboard(lang))
