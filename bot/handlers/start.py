"""/start command and onboarding flow handler."""

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.onboarding import OnboardingStates
from bot.keyboards.main_menu import (
    get_language_keyboard,
    get_family_status_keyboard,
    get_currency_keyboard,
    get_skip_keyboard,
    get_main_menu,
)
from database.repositories.user_repo import UserRepository
from database.repositories.category_repo import CategoryRepository
from database.repositories.wallet_repo import WalletRepository
from database.repositories.budget_repo import BudgetRepository
from bot.utils.formatters import format_money

logger = logging.getLogger(__name__)

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    """Handle /start command."""
    # Always clear any active state first
    await state.clear()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)

    if user and user.is_onboarded:
        # Existing user — show main menu
        lang = user.language
        if lang == "ru":
            text = (
                f"👋 С возвращением, <b>{user.first_name}</b>!\n\n"
                "Выберите действие из меню ниже:"
            )
        else:
            text = (
                f"👋 Qaytganingizdan xursandmiz, <b>{user.first_name}</b>!\n\n"
                "Quyidagi menuyudan kerakli amalni tanlang:"
            )
        await message.answer(text, reply_markup=get_main_menu(lang))
        return

    # New user — start onboarding
    welcome_text = (
        "🤖 <b>MoliyaBot</b>ga xush kelibsiz!\n\n"
        "Men sizga kunlik xarajatlaringizni boshqarishda yordam beraman.\n\n"
        "🌐 Avval tilni tanlang:\n\n"
        "────────────────────\n\n"
        "🤖 Добро пожаловать в <b>MoliyaBot</b>!\n\n"
        "Я помогу вам управлять ежедневными расходами.\n\n"
        "🌐 Выберите язык:"
    )

    await message.answer(welcome_text, reply_markup=get_language_keyboard())
    await state.set_state(OnboardingStates.waiting_language)


# ── Step 1: Language Selection ──────────────────────────────────────
@router.message(OnboardingStates.waiting_language)
async def process_language(message: Message, state: FSMContext, session: AsyncSession):
    """Process language selection."""
    if not message.text:
        await message.answer("⚠️ Tugmalardan birini tanlang:", reply_markup=get_language_keyboard())
        return

    text = message.text

    if "O'zbek" in text or "ozbek" in text.lower():
        lang = "uz"
    elif "Русский" in text or "русский" in text.lower():
        lang = "ru"
    else:
        await message.answer(
            "⚠️ Iltimos, quyidagi tugmalardan birini tanlang:\n"
            "⚠️ Пожалуйста, выберите одну из кнопок:",
            reply_markup=get_language_keyboard(),
        )
        return

    await state.update_data(language=lang)

    # Ask for name
    if lang == "ru":
        text_msg = "👤 Как вас зовут?"
    else:
        text_msg = "👤 Ismingizni kiriting:"

    await message.answer(text_msg)
    await state.set_state(OnboardingStates.waiting_name)


# ── Step 2: Name ────────────────────────────────────────────────────
@router.message(OnboardingStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    """Process name input."""
    if not message.text:
        data = await state.get_data()
        lang = data.get("language", "uz")
        await message.answer("⚠️ Ism kiriting:" if lang == "uz" else "⚠️ Введите имя:")
        return

    name = message.text.strip()
    if len(name) < 2 or len(name) > 50:
        data = await state.get_data()
        lang = data.get("language", "uz")
        if lang == "ru":
            await message.answer("⚠️ Имя должно быть от 2 до 50 символов.")
        else:
            await message.answer("⚠️ Ism 2 dan 50 belgigacha bo'lishi kerak.")
        return

    data = await state.get_data()
    lang = data.get("language", "uz")
    await state.update_data(first_name=name)

    # Ask family status
    if lang == "ru":
        text = f"👋 Приятно познакомиться, <b>{name}</b>!\n\n👥 Ваш семейный статус:"
    else:
        text = f"👋 Tanishganimdan xursandman, <b>{name}</b>!\n\n👥 Oilaviy holatingiz:"

    await message.answer(text, reply_markup=get_family_status_keyboard(lang))
    await state.set_state(OnboardingStates.waiting_family_status)


# ── Step 3: Family Status ──────────────────────────────────────────
@router.message(OnboardingStates.waiting_family_status)
async def process_family_status(message: Message, state: FSMContext):
    """Process family status selection."""
    if not message.text:
        data = await state.get_data()
        lang = data.get("language", "uz")
        await message.answer("⚠️ Tugmalardan birini tanlang:", reply_markup=get_family_status_keyboard(lang))
        return

    text = message.text
    data = await state.get_data()
    lang = data.get("language", "uz")

    if "Yolg'iz" in text or "Один" in text or "Одна" in text:
        status = "single"
    elif "Oilaviy" in text or "Семейный" in text:
        status = "family"
    else:
        await message.answer("⚠️ Tugmalardan birini tanlang:", reply_markup=get_family_status_keyboard(lang))
        return

    await state.update_data(family_status=status)

    # Ask currency
    if lang == "ru":
        text_msg = "💱 Выберите основную валюту:"
    else:
        text_msg = "💱 Asosiy valyutani tanlang:"

    await message.answer(text_msg, reply_markup=get_currency_keyboard())
    await state.set_state(OnboardingStates.waiting_currency)


# ── Step 4: Currency ────────────────────────────────────────────────
@router.message(OnboardingStates.waiting_currency)
async def process_currency(message: Message, state: FSMContext):
    """Process currency selection."""
    if not message.text:
        await message.answer("⚠️ Valyutani tanlang:", reply_markup=get_currency_keyboard())
        return

    text = message.text
    data = await state.get_data()
    lang = data.get("language", "uz")

    if "UZS" in text or "So'm" in text or "Сум" in text:
        currency = "UZS"
    elif "USD" in text or "Dollar" in text:
        currency = "USD"
    elif "EUR" in text or "Yevro" in text or "Евро" in text:
        currency = "EUR"
    else:
        await message.answer("⚠️ Tugmalardan birini tanlang:", reply_markup=get_currency_keyboard())
        return

    await state.update_data(currency=currency)

    # Ask monthly income
    if lang == "ru":
        text_msg = "💰 Введите вашу ежемесячную зарплату (только цифры):\n\nНапример: <code>3500000</code>"
    else:
        text_msg = "💰 Oylik maoshingizni kiriting (faqat raqam):\n\nMasalan: <code>3500000</code>"

    await message.answer(text_msg, reply_markup=get_skip_keyboard(lang))
    await state.set_state(OnboardingStates.waiting_monthly_income)


# ── Step 5: Monthly Income ──────────────────────────────────────────
@router.message(OnboardingStates.waiting_monthly_income)
async def process_monthly_income(message: Message, state: FSMContext):
    """Process monthly income input."""
    if not message.text:
        return

    text = message.text.strip()
    data = await state.get_data()
    lang = data.get("language", "uz")

    # Handle skip
    if "O'tkazib" in text or "Пропустить" in text or "tkazib" in text.lower():
        income = 0
    else:
        # Clean and parse number
        cleaned = text.replace(" ", "").replace(",", "").replace(".", "")
        # Remove common text
        for word in ["so'm", "сум", "sum", "UZS", "$", "€"]:
            cleaned = cleaned.replace(word, "")
        try:
            income = float(cleaned)
            if income < 0:
                income = 0
        except ValueError:
            if lang == "ru":
                await message.answer("⚠️ Введите только цифры. Например: <code>3500000</code>")
            else:
                await message.answer("⚠️ Faqat raqam kiriting. Masalan: <code>3500000</code>")
            return

    await state.update_data(monthly_income=income)

    # If family — ask spouse income
    if data.get("family_status") == "family":
        if lang == "ru":
            text_msg = "💰 Введите зарплату второго члена семьи (только цифры):"
        else:
            text_msg = "💰 Ikkinchi oila a'zosining oyligini kiriting (faqat raqam):"
        await message.answer(text_msg, reply_markup=get_skip_keyboard(lang))
        await state.set_state(OnboardingStates.waiting_monthly_income_2)
    else:
        # Skip to budget
        await ask_budget(message, state)


@router.message(OnboardingStates.waiting_monthly_income_2)
async def process_monthly_income_2(message: Message, state: FSMContext):
    """Process spouse's monthly income."""
    if not message.text:
        return

    text = message.text.strip()
    data = await state.get_data()
    lang = data.get("language", "uz")

    if "O'tkazib" in text or "Пропустить" in text or "tkazib" in text.lower():
        income_2 = 0
    else:
        cleaned = text.replace(" ", "").replace(",", "").replace(".", "")
        for word in ["so'm", "сум", "sum", "UZS", "$", "€"]:
            cleaned = cleaned.replace(word, "")
        try:
            income_2 = float(cleaned)
            if income_2 < 0:
                income_2 = 0
        except ValueError:
            if lang == "ru":
                await message.answer("⚠️ Введите только цифры.")
            else:
                await message.answer("⚠️ Faqat raqam kiriting.")
            return

    await state.update_data(monthly_income_2=income_2)
    await ask_budget(message, state)


async def ask_budget(message: Message, state: FSMContext):
    """Ask for monthly budget."""
    data = await state.get_data()
    lang = data.get("language", "uz")
    income = data.get("monthly_income", 0)
    income_2 = data.get("monthly_income_2", 0)
    total = income + income_2
    currency = data.get("currency", "UZS")

    suggested = int(total * 0.8) if total > 0 else 0

    if lang == "ru":
        text = (
            f"📊 Общий доход: {format_money(total, currency)}\n\n"
            f"🎯 Установите ежемесячный бюджет расходов.\n"
        )
        if suggested > 0:
            text += f"Рекомендуем: <code>{suggested}</code>\n\n"
        text += "Введите сумму бюджета:"
    else:
        text = (
            f"📊 Umumiy daromad: {format_money(total, currency)}\n\n"
            f"🎯 Oylik xarajat byudjetini belgilang.\n"
        )
        if suggested > 0:
            text += f"Tavsiya: <code>{suggested}</code>\n\n"
        text += "Byudjet summasini kiriting:"

    await message.answer(text, reply_markup=get_skip_keyboard(lang))
    await state.set_state(OnboardingStates.waiting_budget)


# ── Step 6: Budget ──────────────────────────────────────────────────
@router.message(OnboardingStates.waiting_budget)
async def process_budget(message: Message, state: FSMContext, session: AsyncSession):
    """Process budget and complete onboarding."""
    if not message.text:
        return

    text = message.text.strip()
    data = await state.get_data()
    lang = data.get("language", "uz")

    if "O'tkazib" in text or "Пропустить" in text or "tkazib" in text.lower():
        budget = 0
    else:
        cleaned = text.replace(" ", "").replace(",", "").replace(".", "")
        for word in ["so'm", "сум", "sum", "UZS", "$", "€"]:
            cleaned = cleaned.replace(word, "")
        try:
            budget = float(cleaned)
            if budget < 0:
                budget = 0
        except ValueError:
            if lang == "ru":
                await message.answer("⚠️ Введите только цифры.")
            else:
                await message.answer("⚠️ Faqat raqam kiriting.")
            return

    # ── Save everything to database ──────────────────────────────
    user_repo = UserRepository(session)
    cat_repo = CategoryRepository(session)
    wallet_repo = WalletRepository(session)

    # Create or update user
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    user_data = dict(
        first_name=data["first_name"],
        language=data["language"],
        currency=data.get("currency", "UZS"),
        family_status=data.get("family_status", "single"),
        monthly_income=data.get("monthly_income", 0),
        monthly_income_2=data.get("monthly_income_2", 0),
        is_onboarded=True,
    )

    if user:
        await user_repo.update_user(message.from_user.id, **user_data)
    else:
        user = await user_repo.create_user(
            telegram_id=message.from_user.id,
            first_name=data["first_name"],
            username=message.from_user.username,
            language=data["language"],
        )
        await user_repo.update_user(message.from_user.id, **user_data)

    # Create default categories (only if they don't exist)
    existing_cats = await cat_repo.get_user_categories(message.from_user.id, active_only=False)
    if not existing_cats:
        await cat_repo.create_default_categories(message.from_user.id)

    # Create default wallet (only if doesn't exist)
    from database.repositories.wallet_repo import WalletRepository as WR
    existing_wallets = await wallet_repo.get_user_wallets(message.from_user.id)
    if not existing_wallets:
        await wallet_repo.create_default_wallet(message.from_user.id)

    # Set budget if provided
    if budget > 0:
        from datetime import date
        budget_repo = BudgetRepository(session)
        today = date.today()
        await budget_repo.set_overall_budget(
            message.from_user.id, budget, today.month, today.year
        )

    # Clear FSM state
    await state.clear()

    # Send completion message
    currency = data.get("currency", "UZS")
    if lang == "ru":
        completion_text = (
            "🎉 <b>Регистрация завершена!</b>\n\n"
            f"👤 Имя: {data['first_name']}\n"
            f"💱 Валюта: {currency}\n"
            f"💰 Доход: {format_money(data.get('monthly_income', 0), currency)}\n"
            f"🎯 Бюджет: {format_money(budget, currency)}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>Как пользоваться:</b>\n\n"
            "1️⃣ Просто напишите свои расходы:\n"
            "   <i>«продукты 45000, такси 12000»</i>\n\n"
            "2️⃣ Бот автоматически определит категорию\n\n"
            "3️⃣ Запросите отчёт в любое время\n\n"
            "Начнём! 🚀"
        )
    else:
        completion_text = (
            "🎉 <b>Ro'yxatdan o'tish yakunlandi!</b>\n\n"
            f"👤 Ism: {data['first_name']}\n"
            f"💱 Valyuta: {currency}\n"
            f"💰 Daromad: {format_money(data.get('monthly_income', 0), currency)}\n"
            f"🎯 Byudjet: {format_money(budget, currency)}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>Qanday foydalanish:</b>\n\n"
            "1️⃣ Xarajatingizni oddiy yozing:\n"
            "   <i>«ovqatga 45000, taksi 12000 ketdi»</i>\n\n"
            "2️⃣ Bot avtomatik kategoriyaga ajratadi\n\n"
            "3️⃣ Istalgan vaqt hisobot so'rang\n\n"
            "Boshladik! 🚀"
        )

    await message.answer(completion_text, reply_markup=get_main_menu(lang))
    logger.info(f"New user onboarded: {message.from_user.id} ({data['first_name']})")
