"""Bot handlers package — registers all routers.

IMPORTANT: Router order matters! In aiogram 3.x, the first matching handler
across all routers CONSUMES the message. So:
- Specific handlers (exact text match) must come FIRST
- Generic handlers (F.text catch-all) must come LAST

The catchall router has an F.text handler that catches any text with numbers
as a potential expense. It MUST be last, or it will block all other handlers.
"""

from aiogram import Router

from bot.handlers.start import router as start_router
from bot.handlers.expenses import router as expenses_router
from bot.handlers.income import router as income_router
from bot.handlers.reports import router as reports_router
from bot.handlers.categories import router as categories_router
from bot.handlers.settings import router as settings_router
from bot.handlers.catchall import router as catchall_router


def register_all_routers(parent_router: Router) -> None:
    """Register all handler routers in correct order.
    
    Order is CRITICAL — first match wins, message is consumed.
    """
    # 1. Start/onboarding — highest priority (CommandStart filter)
    parent_router.include_router(start_router)
    # 2. Expense — FSM state handlers + button handlers
    parent_router.include_router(expenses_router)
    # 3. Income — button + FSM state handlers
    parent_router.include_router(income_router)
    # 4. Reports — button + text regex
    parent_router.include_router(reports_router)
    # 5. Categories — text regex commands
    parent_router.include_router(categories_router)
    # 6. Settings — language/currency + placeholder handlers
    parent_router.include_router(settings_router)
    # 7. Catch-all — MUST BE LAST! Catches text with numbers as expenses
    parent_router.include_router(catchall_router)
