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


from aiohttp import web
from pathlib import Path

async def index_handler(request):
    """Serve the React index.html"""
    return web.FileResponse(Path(__file__).parent / 'webapp' / 'dist' / 'index.html')

async def start_web_app():
    """Start the aiohttp web server to serve the React Mini App"""
    app = web.Application()
    
    # Routes for frontend
    app.router.add_get('/', index_handler)
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
