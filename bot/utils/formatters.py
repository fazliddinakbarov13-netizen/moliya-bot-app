"""Formatting utilities for displaying data."""

from bot.utils.constants import (
    CURRENCY_SYMBOLS,
    PROGRESS_FULL,
    PROGRESS_EMPTY,
    PROGRESS_LENGTH,
    MONTH_NAMES_UZ,
    MONTH_NAMES_RU,
)


def format_money(amount: float, currency: str = "UZS") -> str:
    """Format amount with currency symbol.

    Examples:
        format_money(45000) -> "45,000 so'm"
        format_money(100.50, "USD") -> "$100.50"
    """
    symbol = CURRENCY_SYMBOLS.get(currency, "so'm")

    if currency == "UZS":
        # UZS doesn't use decimals
        formatted = f"{int(amount):,}".replace(",", " ")
        return f"{formatted} {symbol}"
    else:
        formatted = f"{amount:,.2f}"
        return f"{symbol}{formatted}"


def progress_bar(current: float, total: float) -> str:
    """Generate a text progress bar.

    Example: ████████░░░░░░░ 53%
    """
    if total <= 0:
        return f"{PROGRESS_EMPTY * PROGRESS_LENGTH} 0%"

    percent = min(100, (current / total) * 100)
    filled = int(PROGRESS_LENGTH * (percent / 100))
    empty = PROGRESS_LENGTH - filled

    # Choose color emoji based on percentage
    if percent >= 100:
        indicator = "🔴"
    elif percent >= 80:
        indicator = "🟡"
    else:
        indicator = "🟢"

    bar = PROGRESS_FULL * filled + PROGRESS_EMPTY * empty
    return f"{bar} {percent:.0f}% {indicator}"


def format_percent(value: float) -> str:
    """Format a percentage value."""
    return f"{value:.1f}%"


def get_month_name(month: int, lang: str = "uz") -> str:
    """Get month name by number and language."""
    if lang == "ru":
        return MONTH_NAMES_RU.get(month, str(month))
    return MONTH_NAMES_UZ.get(month, str(month))


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_category_list(categories: list, lang: str = "uz") -> str:
    """Format a list of categories for display."""
    lines = []
    for i, cat in enumerate(categories, 1):
        name = cat.name_uz if lang == "uz" else cat.name_ru
        status = "✅" if cat.is_active else "❌"
        default = " (standart)" if cat.is_default else ""
        lines.append(f"{i}. {cat.icon} {name}{default} {status}")
    return "\n".join(lines)


def format_transaction_summary(
    expenses_by_category: list[dict],
    total_expenses: float,
    total_income: float,
    budget: float,
    currency: str = "UZS",
    lang: str = "uz",
) -> str:
    """Format a monthly summary report."""
    balance = total_income - total_expenses

    lines = [
        "📊 <b>Oylik hisobot</b>" if lang == "uz" else "📊 <b>Месячный отчёт</b>",
        "",
        f"💰 {'Daromad' if lang == 'uz' else 'Доход'}: {format_money(total_income, currency)}",
        f"💸 {'Xarajat' if lang == 'uz' else 'Расход'}: {format_money(total_expenses, currency)}",
        f"{'📈' if balance >= 0 else '📉'} {'Qoldiq' if lang == 'uz' else 'Остаток'}: {format_money(balance, currency)}",
        "",
    ]

    # Budget progress
    if budget > 0:
        bar_label = "Byudjet" if lang == "uz" else "Бюджет"
        lines.append(f"🎯 {bar_label}: {progress_bar(total_expenses, budget)}")
        lines.append(
            f"   {format_money(total_expenses, currency)} / {format_money(budget, currency)}"
        )
        lines.append("")

    # Category breakdown
    if expenses_by_category:
        header = "📋 Kategoriya bo'yicha:" if lang == "uz" else "📋 По категориям:"
        lines.append(f"<b>{header}</b>")
        lines.append("")

        for cat_data in expenses_by_category:
            name = cat_data["name"]
            icon = cat_data["icon"]
            total = cat_data["total"]
            percent = (total / total_expenses * 100) if total_expenses > 0 else 0
            lines.append(
                f"  {icon} {name}: {format_money(total, currency)} ({format_percent(percent)})"
            )

    return "\n".join(lines)
