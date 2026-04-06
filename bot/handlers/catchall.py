"""Catch-all handler for direct expense text input.

THIS MUST BE THE LAST ROUTER REGISTERED — it catches any text with numbers
that wasn't handled by other routers, and processes it as an expense.

In aiogram 3.x, the first matching handler consumes the message.
That's why this MUST be in a separate router registered after all others.
"""

import re
import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.expense import ExpenseStates
from bot.handlers.expenses import process_expense_input
from database.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)

router = Router(name="catchall")


@router.message(F.text)
async def direct_expense_input(message: Message, state: FSMContext, session: AsyncSession):
    """Handle direct expense text with numbers (no need to press button first).
    
    IMPORTANT: This router must be registered LAST so it doesn't block
    other handlers from processing menu buttons and commands.
    """
    # Don't intercept if in any FSM state
    current_state = await state.get_state()
    if current_state is not None:
        return

    # Check if user exists and is onboarded
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_onboarded:
        return

    text = message.text

    # Skip short text
    if len(text) < 3:
        return

    # Skip if it starts with any known emoji/menu prefix or command
    skip_chars = [
        "📝", "📊", "🎯", "💳", "💰", "👛", "🤝", "⚙️",
        "🌐", "💱", "📂", "🔔", "🔄", "👨", "🔙",
        "/", "❌", "✅", "⏭", "🇺🇿", "🇷🇺", "🇺🇸", "🇪🇺",
        "💼", "📈", "💵",  # income type buttons
    ]
    if any(text.startswith(c) for c in skip_chars):
        return

    # Must have at least one number >= 100 (reasonable expense)
    has_expense_amount = bool(re.search(r'\d{3,}', text))
    if not has_expense_amount:
        return

    # Process as expense
    await state.set_state(ExpenseStates.waiting_input)
    await process_expense_input(message, state, session)
