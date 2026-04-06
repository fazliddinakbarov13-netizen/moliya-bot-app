"""Expense entry handler with AI categorization."""

import logging
import re
from datetime import date, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.expense import ExpenseStates
from bot.keyboards.main_menu import get_main_menu, get_cancel_keyboard
from bot.keyboards.inline import get_expense_confirm_keyboard, get_category_select_keyboard
from bot.services.ai_service import categorize_expense
from bot.utils.formatters import format_money
from database.repositories.user_repo import UserRepository
from database.repositories.category_repo import CategoryRepository
from database.repositories.transaction_repo import TransactionRepository
from database.repositories.wallet_repo import WalletRepository
from database.repositories.budget_repo import BudgetRepository
from bot.utils.constants import BUDGET_WARNING_PERCENT

logger = logging.getLogger(__name__)

router = Router(name="expenses")


# ── Global cancel handler — works in ANY expense state ──────────────
# This catches "Bekor" text from reply keyboard while in confirm/category states
@router.message(ExpenseStates.waiting_confirm, F.text)
async def handle_text_in_confirm(message: Message, state: FSMContext, session: AsyncSession):
    """Handle ANY text message while waiting for confirm (user should use inline buttons).
    If it's cancel — cancel. Otherwise remind to use buttons."""
    if "Bekor" in message.text or "Отмена" in message.text:
        await state.clear()
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "uz"
        await message.answer("❌ Bekor qilindi." if lang == "uz" else "❌ Отменено.", reply_markup=get_main_menu(lang))
    else:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "uz"
        if lang == "ru":
            await message.answer("⬆️ Используйте кнопки выше: подтвердить, изменить или отменить.")
        else:
            await message.answer("⬆️ Yuqoridagi tugmalarni ishlating: tasdiqlash, tahrirlash yoki bekor qilish.")


@router.message(ExpenseStates.waiting_category, F.text)
async def handle_text_in_category(message: Message, state: FSMContext, session: AsyncSession):
    """Handle text while waiting for category selection."""
    if "Bekor" in message.text or "Отмена" in message.text:
        await state.clear()
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "uz"
        await message.answer("❌ Bekor qilindi." if lang == "uz" else "❌ Отменено.", reply_markup=get_main_menu(lang))
    else:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "uz"
        if lang == "ru":
            await message.answer("⬆️ Выберите категорию из списка выше.")
        else:
            await message.answer("⬆️ Yuqoridagi ro'yxatdan kategoriyani tanlang.")


# ── Trigger: "📝 Xarajat" button ───────────────────────────────────
@router.message(F.text.in_(["📝 Xarajat", "📝 Расход"]))
async def expense_button(message: Message, state: FSMContext, session: AsyncSession):
    """Handle expense button press — enter expense entry mode."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return

    lang = user.language

    if lang == "ru":
        text = (
            "📝 <b>Введите расход:</b>\n\n"
            "Просто напишите что и сколько потратили:\n\n"
            "• <i>продукты 45000</i>\n"
            "• <i>такси 12000, обед 25000</i>\n"
            "• <i>вчера аптека 80000</i>\n\n"
            "Я автоматически определю категорию! 🤖"
        )
    else:
        text = (
            "📝 <b>Xarajat kiriting:</b>\n\n"
            "Oddiy yozing, nima uchun qancha ketdi:\n\n"
            "• <i>ovqatga 45000</i>\n"
            "• <i>taksi 12000, tushlik 25000</i>\n"
            "• <i>kecha dorixonaga 80000 ketdi</i>\n\n"
            "Bot avtomatik kategoriyaga ajratadi! 🤖"
        )

    await message.answer(text, reply_markup=get_cancel_keyboard(lang))
    await state.set_state(ExpenseStates.waiting_input)


# ── Process expense text ────────────────────────────────────────────
@router.message(ExpenseStates.waiting_input, F.text)
async def process_expense_input(message: Message, state: FSMContext, session: AsyncSession):
    """Process expense text input — send to AI for categorization."""
    text = message.text

    # Handle cancel
    if "Bekor" in text or "Отмена" in text:
        await state.clear()
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        lang = user.language if user else "uz"
        await message.answer("❌ Bekor qilindi." if lang == "uz" else "❌ Отменено.", reply_markup=get_main_menu(lang))
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        await state.clear()
        await message.answer("Xatolik. /start buyrug'ini yuboring.")
        return

    lang = user.language
    currency = user.currency

    # Get user categories
    cat_repo = CategoryRepository(session)
    categories = await cat_repo.get_user_categories(message.from_user.id)

    if not categories:
        await state.clear()
        await message.answer(
            "⚠️ Kategoriyalaringiz yo'q. /start buyrug'ini yuboring." if lang == "uz"
            else "⚠️ У вас нет категорий. Используйте /start для настройки.",
            reply_markup=get_main_menu(lang),
        )
        return

    # Build category list for AI
    cat_list = [{"id": c.id, "name": c.name, "icon": c.icon} for c in categories]

    # Show processing message
    processing = await message.answer(
        "🤖 Xarajatingizni tahlil qilmoqdaman..." if lang == "uz"
        else "🤖 Анализирую ваш расход..."
    )

    # Send to AI
    try:
        parsed_expenses = await categorize_expense(text, cat_list, lang)
    except Exception as e:
        logger.error(f"AI error for user {message.from_user.id}: {e}", exc_info=True)
        parsed_expenses = []

    if not parsed_expenses:
        # AI failed — offer manual category selection
        await state.update_data(manual_amount_text=text)
        await processing.edit_text(
            "🤔 Kategoriyani avtomatik aniqlab bo'lmadi.\nKategoriyani qo'lda tanlang:" if lang == "uz"
            else "🤔 Не удалось определить категорию автоматически.\nВыберите категорию вручную:",
            reply_markup=get_category_select_keyboard(categories, lang),
        )
        await state.set_state(ExpenseStates.waiting_category)
        return

    # Filter out zero/negative amounts
    parsed_expenses = [e for e in parsed_expenses if e.get("amount", 0) > 0]
    if not parsed_expenses:
        await state.clear()
        await processing.edit_text(
            "🤔 Xarajat summasi topilmadi. Summani raqam bilan kiriting." if lang == "uz"
            else "🤔 Не найдена сумма расхода. Укажите сумму цифрами."
        )
        return

    # Format parsed expenses for confirmation
    lines = []
    total = 0
    for exp in parsed_expenses:
        amount = exp.get("amount", 0)
        cat_name = exp.get("category_name", "Noma'lum")
        icon = exp.get("icon", "📦")
        desc = exp.get("description", "")
        total += amount

        line = f"  {icon} {cat_name}: {format_money(amount, currency)}"
        if desc:
            line += f" ({desc})"
        lines.append(line)

    # Check date offset
    date_info = ""
    for exp in parsed_expenses:
        offset = exp.get("date_offset", 0)
        if offset == -1:
            date_info = " (kecha)" if lang == "uz" else " (вчера)"
            break

    exp_list = "\n".join(lines)
    if lang == "ru":
        confirm_text = (
            f"📋 <b>Найденные расходы{date_info}:</b>\n\n"
            f"{exp_list}\n\n"
            f"💰 Итого: <b>{format_money(total, currency)}</b>\n\n"
            "Подтвердите или измените:"
        )
    else:
        confirm_text = (
            f"📋 <b>Topilgan xarajatlar{date_info}:</b>\n\n"
            f"{exp_list}\n\n"
            f"💰 Jami: <b>{format_money(total, currency)}</b>\n\n"
            "Tasdiqlang yoki o'zgartiring:"
        )

    # Save parsed expenses to FSM state
    await state.update_data(parsed_expenses=parsed_expenses, original_text=text)

    await processing.edit_text(
        confirm_text,
        reply_markup=get_expense_confirm_keyboard(parsed_expenses, lang),
    )
    await state.set_state(ExpenseStates.waiting_confirm)


# ── Confirm expense ─────────────────────────────────────────────────
@router.callback_query(F.data == "expense_confirm")
async def confirm_expense(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Save confirmed expenses to database."""
    data = await state.get_data()
    parsed_expenses = data.get("parsed_expenses", [])

    if not parsed_expenses:
        await callback.answer("Xarajatlar topilmadi")
        await state.clear()
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Xatolik")
        await state.clear()
        return

    lang = user.language
    currency = user.currency
    trans_repo = TransactionRepository(session)
    wallet_repo = WalletRepository(session)
    budget_repo = BudgetRepository(session)

    default_wallet = await wallet_repo.get_default_wallet(callback.from_user.id)

    saved_count = 0
    total_saved = 0

    for exp in parsed_expenses:
        amount = exp.get("amount", 0)
        category_id = exp.get("category_id")
        description = exp.get("description", "")
        date_offset = exp.get("date_offset", 0)

        trans_date = date.today() + timedelta(days=date_offset)

        try:
            await trans_repo.add_expense(
                user_id=callback.from_user.id,
                amount=amount,
                category_id=category_id,
                description=description,
                transaction_date=trans_date,
                wallet_id=default_wallet.id if default_wallet else None,
            )

            if default_wallet:
                await wallet_repo.update_balance(default_wallet.id, amount, is_expense=True)

            saved_count += 1
            total_saved += amount
        except Exception as e:
            logger.error(f"Error saving expense: {e}", exc_info=True)

    if saved_count == 0:
        await callback.message.edit_text("❌ Xarajat saqlanmadi. Qayta urinib ko'ring.")
        await state.clear()
        await callback.answer()
        return

    # Check budget warnings
    today = date.today()
    budget_warning = ""
    try:
        overall_budget = await budget_repo.get_overall_budget(
            callback.from_user.id, today.month, today.year
        )
        if overall_budget and overall_budget.amount > 0:
            month_total = await trans_repo.get_monthly_expense_total(
                callback.from_user.id, today.month, today.year
            )
            percent = (month_total / overall_budget.amount) * 100

            if percent >= 100:
                budget_warning = f"\n\n🔴 <b>{'Byudjet oshib ketdi' if lang == 'uz' else 'Бюджет превышен'}!</b> ({percent:.0f}%)"
            elif percent >= BUDGET_WARNING_PERCENT:
                budget_warning = f"\n\n🟡 <b>{'Byudjetning' if lang == 'uz' else 'Использовано'} {percent:.0f}% {'sarflandi' if lang == 'uz' else 'бюджета'}</b>"
    except Exception as e:
        logger.error(f"Budget check error: {e}")

    # Success message
    if lang == "ru":
        success = f"✅ Сохранено <b>{saved_count}</b> расход(ов) на сумму <b>{format_money(total_saved, currency)}</b>{budget_warning}"
    else:
        success = f"✅ <b>{saved_count}</b> ta xarajat saqlandi, jami <b>{format_money(total_saved, currency)}</b>{budget_warning}"

    await callback.message.edit_text(success)
    await state.clear()
    await callback.answer("✅ Saqlandi!")
    logger.info(f"User {callback.from_user.id} saved {saved_count} expenses, total: {total_saved}")


# ── Cancel expense (inline button) ──────────────────────────────────
@router.callback_query(F.data == "expense_cancel")
async def cancel_expense(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Cancel expense entry."""
    await state.clear()
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language if user else "uz"
    await callback.message.edit_text("❌ Bekor qilindi." if lang == "uz" else "❌ Отменено.")
    await callback.answer()


# ── Cancel from category selection (inline) ─────────────────────────
@router.callback_query(F.data == "cat_cancel")
async def cancel_category_select(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Cancel category selection."""
    await state.clear()
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language if user else "uz"
    await callback.message.edit_text("❌ Bekor qilindi." if lang == "uz" else "❌ Отменено.")
    await callback.answer()


# ── Manual category selection ───────────────────────────────────────
@router.callback_query(F.data.startswith("cat_select:"))
async def manual_category_selected(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Handle manual category selection after AI failure or edit."""
    try:
        category_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("Xatolik")
        return

    data = await state.get_data()

    # Check if editing an AI-parsed expense
    parsed_expenses = data.get("parsed_expenses", [])
    if parsed_expenses:
        # Update the first expense category and auto-confirm
        parsed_expenses[0]["category_id"] = category_id
        await state.update_data(parsed_expenses=parsed_expenses)
        await confirm_expense(callback, state, session)
        return

    # Manual flow — extract amount from original text
    original_text = data.get("manual_amount_text", "")
    numbers = re.findall(r'\d[\d\s,]*\d|\d+', original_text)
    amount = 0
    for num_str in numbers:
        cleaned = num_str.replace(" ", "").replace(",", "")
        try:
            val = float(cleaned)
            if val >= 100:  # Minimum reasonable expense amount
                amount = val
                break
        except ValueError:
            continue

    if amount <= 0:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        lang = user.language if user else "uz"
        await callback.message.edit_text(
            "⚠️ Summani aniqlab bo'lmadi. Qayta kiriting." if lang == "uz"
            else "⚠️ Не удалось определить сумму. Попробуйте снова."
        )
        await state.clear()
        await callback.answer()
        return

    # Save directly
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await state.clear()
        await callback.answer("Xatolik")
        return

    lang = user.language
    currency = user.currency
    trans_repo = TransactionRepository(session)
    wallet_repo = WalletRepository(session)

    default_wallet = await wallet_repo.get_default_wallet(callback.from_user.id)

    try:
        await trans_repo.add_expense(
            user_id=callback.from_user.id,
            amount=amount,
            category_id=category_id,
            description=original_text[:100],
            transaction_date=date.today(),
            wallet_id=default_wallet.id if default_wallet else None,
        )

        if default_wallet:
            await wallet_repo.update_balance(default_wallet.id, amount, is_expense=True)
    except Exception as e:
        logger.error(f"Error saving manual expense: {e}", exc_info=True)
        await callback.message.edit_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
        await state.clear()
        await callback.answer()
        return

    # Get category name for display
    cat_repo = CategoryRepository(session)
    category = await cat_repo.get_by_id(category_id)
    cat_name = category.name if category else "Noma'lum"
    cat_icon = category.icon if category else "📦"

    await state.clear()

    success = f"✅ Saqlandi: {cat_icon} {cat_name} — <b>{format_money(amount, currency)}</b>" if lang == "uz" \
        else f"✅ Сохранено: {cat_icon} {cat_name} — <b>{format_money(amount, currency)}</b>"

    await callback.message.edit_text(success)
    await callback.answer("✅ Saqlandi!")
    logger.info(f"User {callback.from_user.id} manual expense: {amount} -> {cat_name}")


# ── Edit expense — switch to category selection ─────────────────────
@router.callback_query(F.data == "expense_edit")
async def edit_expense(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Show category selection for manual edit."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Xatolik")
        return

    lang = user.language
    cat_repo = CategoryRepository(session)
    categories = await cat_repo.get_user_categories(callback.from_user.id)

    text = "📂 To'g'ri kategoriyani tanlang:" if lang == "uz" else "📂 Выберите правильную категорию:"

    await callback.message.edit_text(text, reply_markup=get_category_select_keyboard(categories, lang))
    await state.set_state(ExpenseStates.waiting_category)
    await callback.answer()


