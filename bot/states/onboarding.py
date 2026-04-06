"""Onboarding FSM states for new user registration."""

from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """States for the onboarding flow."""

    waiting_language = State()
    waiting_name = State()
    waiting_family_status = State()
    waiting_currency = State()
    waiting_monthly_income = State()
    waiting_monthly_income_2 = State()  # Spouse income (if family)
    waiting_budget = State()
