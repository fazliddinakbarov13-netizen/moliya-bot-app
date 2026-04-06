"""Expense and income entry FSM states."""

from aiogram.fsm.state import State, StatesGroup


class ExpenseStates(StatesGroup):
    """States for expense entry flow."""

    waiting_input = State()  # Waiting for text/voice/photo
    waiting_confirm = State()  # Waiting for confirmation
    waiting_category = State()  # Manual category selection
    waiting_edit_amount = State()  # Editing amount
    waiting_wallet = State()  # Wallet selection


class IncomeStates(StatesGroup):
    """States for income entry flow."""

    waiting_type = State()  # Income type selection
    waiting_amount = State()  # Amount entry
    waiting_description = State()  # Optional description
