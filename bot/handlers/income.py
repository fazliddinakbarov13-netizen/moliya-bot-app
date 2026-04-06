"""Income entry handler."""

import logging
from datetime import date

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.expense import IncomeStates
from bot.keyboards.main_menu import get_main_menu, get_income_type_keyboard, get_cancel_keyboard
from bot.utils.formatters import format_money
from database.repositories.user_repo import UserRepository
from database.repositories.transaction_repo import TransactionRepository
from database.repositories.wallet_repo import WalletRepository

logger = logging.getLogger(__name__)

router = Router(name="income")


@router.message(F.text.in_(["💰 Daromad", "💰 Доход"]))
async def income_button(message: Message, state: FSMContext, session: AsyncSession):
    """Handle income button press."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return

    lang = user.language
    text = "💰 <b>Daromad turini tanlang:</b>" if lang == "uz" else "💰 <b>Выберите тип дохода:</b>"

    await message.answer(text, reply_markup=get_income_type_keyboard(lang))
    await state.set_state(IncomeStates.waiting_type)


@router.message(IncomeStates.waiting_type, F.text)
async def process_income_type(message: Message, state: FSMContext, session: AsyncSession):
    """Process income type selection."""
    text = message.text

    # Handle cancel
    if "Bekor" in text or "Отмена" in text:
        await state.clear()
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "uz"
        await message.answer("❌ Bekor qilindi." if lang == "uz" else "❌ Отменено.", reply_markup=get_main_menu(lang))
        return

    # Determine income type
    if "Oylik" in text or "Зарплата" in text:
        if "Ikkinchi" in text or "2-й" in text:
            income_type = "salary_2"
        else:
            income_type = "salary"
    elif "Qo'shimcha" in text or "Доп" in text or "Дополн" in text:
        income_type = "additional"
    elif "Boshqa" in text or "Прочий" in text or "Другой" in text:
        income_type = "other"
    else:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "uz"
        await message.answer(
            "⚠️ Tugmalardan birini tanlang:" if lang == "uz" else "⚠️ Выберите одну из кнопок:",
            reply_markup=get_income_type_keyboard(lang),
        )
        return

    await state.update_data(income_type=income_type)

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language if user else "uz"

    text_msg = "💰 Daromad summasini kiriting (faqat raqam):\n\nMasalan: <code>3500000</code>" if lang == "uz" \
        else "💰 Введите сумму дохода (только цифры):\n\nНапример: <code>3500000</code>"

    await message.answer(text_msg, reply_markup=get_cancel_keyboard(lang))
    await state.set_state(IncomeStates.waiting_amount)


@router.message(IncomeStates.waiting_amount, F.text)
async def process_income_amount(message: Message, state: FSMContext, session: AsyncSession):
    """Process income amount."""
    text = message.text.strip()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        await state.clear()
        await message.answer("Xatolik. /start buyrug'ini yuboring.")
        return

    lang = user.language
    currency = user.currency

    # Handle cancel
    if "Bekor" in text or "Отмена" in text:
        await state.clear()
        await message.answer("❌ Bekor qilindi." if lang == "uz" else "❌ Отменено.", reply_markup=get_main_menu(lang))
        return

    # Parse amount — remove spaces, commas, currency words
    cleaned = text.replace(" ", "").replace(",", "").replace(".", "")
    for word in ["so'm", "сум", "sum", "UZS", "$", "€"]:
        cleaned = cleaned.replace(word, "")
    try:
        amount = float(cleaned)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        await message.answer("⚠️ Musbat raqam kiriting." if lang == "uz" else "⚠️ Введите положительное число.")
        return

    data = await state.get_data()
    income_type = data.get("income_type", "salary")

    # Type labels
    type_labels = {
        "salary": "Oylik maosh" if lang == "uz" else "Зарплата",
        "salary_2": "Ikkinchi kishi oyligi" if lang == "uz" else "Зарплата (2-й)",
        "additional": "Qo'shimcha daromad" if lang == "uz" else "Доп. доход",
        "other": "Boshqa daromad" if lang == "uz" else "Прочий доход",
    }
    type_label = type_labels.get(income_type, income_type)

    # Save to database
    try:
        trans_repo = TransactionRepository(session)
        wallet_repo = WalletRepository(session)

        await trans_repo.add_income(
            user_id=message.from_user.id,
            amount=amount,
            income_type=income_type,
            description=type_label,
            transaction_date=date.today(),
        )

        default_wallet = await wallet_repo.get_default_wallet(message.from_user.id)
        if default_wallet:
            await wallet_repo.update_balance(default_wallet.id, amount, is_expense=False)

        # Update user's monthly income if salary
        if income_type == "salary":
            await user_repo.update_user(message.from_user.id, monthly_income=amount)
        elif income_type == "salary_2":
            await user_repo.update_user(message.from_user.id, monthly_income_2=amount)

    except Exception as e:
        logger.error(f"Error saving income: {e}", exc_info=True)
        await state.clear()
        await message.answer("❌ Xatolik yuz berdi. Qayta urinib ko'ring.", reply_markup=get_main_menu(lang))
        return

    await state.clear()

    success = (
        f"✅ <b>Daromad saqlandi!</b>\n\n📌 Turi: {type_label}\n💰 Summa: {format_money(amount, currency)}"
        if lang == "uz" else
        f"✅ <b>Доход сохранён!</b>\n\n📌 Тип: {type_label}\n💰 Сумма: {format_money(amount, currency)}"
    )

    await message.answer(success, reply_markup=get_main_menu(lang))
    logger.info(f"User {message.from_user.id} added income: {amount} ({income_type})")
