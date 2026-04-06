"""Monthly reports handler."""

import logging
from datetime import date

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_menu import get_main_menu
from bot.keyboards.inline import get_report_type_keyboard, get_month_select_keyboard
from bot.utils.formatters import format_money, format_transaction_summary, progress_bar, get_month_name
from database.repositories.user_repo import UserRepository
from database.repositories.transaction_repo import TransactionRepository
from database.repositories.budget_repo import BudgetRepository

logger = logging.getLogger(__name__)
router = Router(name="reports")


@router.message(F.text.in_(["📊 Hisobot", "📊 Отчёт"]))
async def report_button(message: Message, session: AsyncSession):
    """Handle report button press."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return

    lang = user.language
    text = "📊 <b>Hisobot turini tanlang:</b>" if lang == "uz" else "📊 <b>Выберите тип отчёта:</b>"
    await message.answer(text, reply_markup=get_report_type_keyboard(lang), parse_mode="HTML")


@router.callback_query(F.data == "report_current")
async def current_month_report(callback: CallbackQuery, session: AsyncSession):
    """Generate current month report."""
    today = date.today()
    await generate_report(callback, session, today.month, today.year)


@router.callback_query(F.data == "report_select_month")
async def select_month(callback: CallbackQuery, session: AsyncSession):
    """Show month selection."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language if user else "uz"
    text = "📅 Oyni tanlang:" if lang == "uz" else "📅 Выберите месяц:"
    await callback.message.edit_text(text, reply_markup=get_month_select_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("month_select:"))
async def month_selected(callback: CallbackQuery, session: AsyncSession):
    """Handle month selection."""
    month = int(callback.data.split(":")[1])
    await generate_report(callback, session, month, date.today().year)


async def generate_report(callback: CallbackQuery, session: AsyncSession, month: int, year: int):
    """Generate and send monthly report."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Xatolik")
        return

    lang = user.language
    currency = user.currency
    trans_repo = TransactionRepository(session)
    budget_repo = BudgetRepository(session)

    total_exp = await trans_repo.get_monthly_expense_total(callback.from_user.id, month, year)
    total_inc = await trans_repo.get_monthly_income_total(callback.from_user.id, month, year)
    by_cat = await trans_repo.get_expenses_by_category(callback.from_user.id, month, year)
    budget = await budget_repo.get_overall_budget(callback.from_user.id, month, year)
    budget_amt = budget.amount if budget else 0

    if total_inc == 0:
        total_inc = (user.monthly_income or 0) + (user.monthly_income_2 or 0)

    balance = total_inc - total_exp
    month_name = get_month_name(month, lang)

    lines = [
        f"📊 <b>{month_name} {year} {'hisoboti' if lang == 'uz' else 'отчёт'}</b>",
        "",
        f"💰 {'Daromad' if lang == 'uz' else 'Доход'}: <b>{format_money(total_inc, currency)}</b>",
        f"💸 {'Xarajat' if lang == 'uz' else 'Расход'}: <b>{format_money(total_exp, currency)}</b>",
        f"{'📈' if balance >= 0 else '📉'} {'Qoldiq' if lang == 'uz' else 'Остаток'}: <b>{format_money(balance, currency)}</b>",
        "",
    ]

    if budget_amt > 0:
        lines.append(f"🎯 {'Byudjet' if lang == 'uz' else 'Бюджет'}:")
        lines.append(f"  {progress_bar(total_exp, budget_amt)}")
        lines.append(f"  {format_money(total_exp, currency)} / {format_money(budget_amt, currency)}")
        lines.append("")

    if by_cat:
        lines.append(f"<b>📋 {'Kategoriyalar' if lang == 'uz' else 'Категории'}:</b>")
        lines.append("")
        for c in by_cat:
            pct = (c['total'] / total_exp * 100) if total_exp > 0 else 0
            lines.append(f"  {c['icon']} {c['name']}: {format_money(c['total'], currency)} ({pct:.1f}%)")
        lines.append("")

    if total_inc > 0:
        sr = (balance / total_inc) * 100
        lines.append(f"💎 {'Tejamkorlik' if lang == 'uz' else 'Сбережения'}: {sr:.1f}%")

    if not by_cat and total_exp == 0:
        lines.append("ℹ️ " + ("Bu oyda xarajatlar yo'q." if lang == "uz" else "В этом месяце нет расходов."))

    await callback.message.edit_text("\n".join(lines), parse_mode="HTML")
    await callback.answer()


@router.message(F.text.regexp(r"(?i)(hisobot|отч[её]т|report)"))
async def text_report(message: Message, session: AsyncSession):
    """Handle text report request like 'Aprel hisoboti'."""
    from bot.utils.constants import MONTH_NAMES_UZ, MONTH_NAMES_RU

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return

    text = message.text.lower()
    month = None

    for num, name in MONTH_NAMES_UZ.items():
        if name.lower() in text:
            month = num
            break
    if not month:
        for num, name in MONTH_NAMES_RU.items():
            if name.lower() in text:
                month = num
                break
    if not month:
        month = date.today().month

    year = date.today().year
    lang = user.language
    currency = user.currency
    trans_repo = TransactionRepository(session)
    budget_repo = BudgetRepository(session)

    total_exp = await trans_repo.get_monthly_expense_total(message.from_user.id, month, year)
    total_inc = await trans_repo.get_monthly_income_total(message.from_user.id, month, year)
    by_cat = await trans_repo.get_expenses_by_category(message.from_user.id, month, year)
    budget = await budget_repo.get_overall_budget(message.from_user.id, month, year)
    budget_amt = budget.amount if budget else 0

    if total_inc == 0:
        total_inc = (user.monthly_income or 0) + (user.monthly_income_2 or 0)

    report = format_transaction_summary(by_cat, total_exp, total_inc, budget_amt, currency, lang)
    month_name = get_month_name(month, lang)
    header = f"📊 <b>{month_name} {year}</b>\n\n"

    await message.answer(header + report, parse_mode="HTML")
