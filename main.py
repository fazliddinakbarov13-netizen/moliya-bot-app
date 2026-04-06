"""MoliyaBot — Telegram AI Finance Bot for Uzbekistan.

Entry point: initializes bot, database, scheduler, and starts polling.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database.engine import init_db, close_db
from bot.handlers import register_all_routers
from bot.middlewares.database import DatabaseMiddleware


# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Reduce noise from libraries
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def on_startup(bot: Bot):
    """Actions to perform on bot startup."""
    logger.info("🚀 MoliyaBot ishga tushmoqda...")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"✅ Bot: @{bot_info.username} ({bot_info.first_name})")
    logger.info("✅ MoliyaBot tayyor!")


async def on_shutdown(bot: Bot):
    """Actions to perform on bot shutdown."""
    logger.info("🛑 MoliyaBot to'xtatilmoqda...")
    await close_db()
    logger.info("✅ Database connection closed")


import json
from aiohttp import web
from pathlib import Path
from database.engine import async_session_maker
from database.repositories.user_repo import UserRepository
from database.repositories.wallet_repo import WalletRepository

async def cors_middleware(app, handler):
    async def middleware_handler(request):
        if request.method == "OPTIONS":
            response = web.Response()
        else:
            response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    return middleware_handler

async def index_handler(request):
    """Serve the React index.html"""
    return web.FileResponse(Path(__file__).parent / 'webapp' / 'dist' / 'index.html')

async def api_get_user(request):
    """Endpoint: Fetch real balance from SQLite"""
    try:
        tg_id = int(request.query.get("tg_id", 0))
    except ValueError:
        return web.json_response({"error": "Invalid tg_id"}, status=400)
        
    if not tg_id:
        return web.json_response({"error": "Missing tg_id"}, status=400)

    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        wallet_repo = WalletRepository(session)
        
        user = await user_repo.get_by_telegram_id(tg_id)
        if not user:
            return web.json_response({"balance": 0.0, "status": "no_user"})
            
        wallets = await wallet_repo.get_user_wallets(user.id)
        total_balance = sum(w.balance for w in wallets)
        
        return web.json_response({"balance": total_balance, "status": "ok"})

from database.repositories.transaction_repo import TransactionRepository
from bot.services.transaction import TransactionService

async def api_post_transaction(request):
    """Endpoint: Post a new transaction and write to DB"""
    try:
        data = await request.json()
        tg_id = int(data.get("tg_id", 0))
        amount = float(data.get("amount", 0))
        is_expense = bool(data.get("is_expense", True))
        
        if not tg_id or amount <= 0:
            return web.json_response({"error": "Invalid data"}, status=400)
            
        async with async_session_maker() as session:
            user_repo = UserRepository(session)
            wallet_repo = WalletRepository(session)
            tx_repo = TransactionRepository(session)
            
            user = await user_repo.get_by_telegram_id(tg_id)
            if not user:
                return web.json_response({"error": "User not found"}, status=404)
                
            wallet = await wallet_repo.get_default_wallet(user.id)
            if not wallet:
                return web.json_response({"error": "No wallet found"}, status=400)
                
            if is_expense and wallet.balance < amount:
                return web.json_response({"error": "Insufficient funds", "success": False})
                
            # Create the transaction
            tx = await tx_repo.create_transaction(
                user_id=user.id,
                wallet_id=wallet.id,
                category_id=None, # Will map specific UI categories later
                amount=amount,
                type="expense" if is_expense else "income",
                description="WebApp orqali",
            )
            # Update physical wallet balance
            await wallet_repo.update_balance(wallet.id, amount, is_expense=is_expense)
            print(f"✅ DB Update: User {tg_id} transacted {amount}. Expense: {is_expense}")
            return web.json_response({"status": "ok", "success": True, "new_balance": wallet.balance})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def start_web_app():
    """Start the aiohttp web server to serve the React Mini App"""
    app = web.Application(middlewares=[cors_middleware])
    
    # Routes for frontend
    app.router.add_get('/', index_handler)
    app.router.add_get('/api/user', api_get_user)
    app.router.add_post('/api/transaction', api_post_transaction)
    app.router.add_static('/', path=Path(__file__).parent / 'webapp' / 'dist', name='webapp')
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8000)
    await site.start()
    logger.info("✅ Web App API ishga tushdi: http://127.0.0.1:8000")

async def main():
    """Main function — start the bot."""
    # Start web server
    asyncio.create_task(start_web_app())

    # Create bot instance
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Create dispatcher with memory storage (for FSM)
    dp = Dispatcher(storage=MemoryStorage())

    # Register startup/shutdown hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Register middleware
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    # Register all handlers
    register_all_routers(dp)

    # Start polling
    logger.info("🔄 Starting polling...")

    try:
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message",
                "callback_query",
                "inline_query",
            ],
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
