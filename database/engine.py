"""Async database engine and session management."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    **({"pool_size": 20, "max_overflow": 10} if not settings.is_sqlite else {}),
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """Get a new database session."""
    async with async_session() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    from database.models.base import Base
    # Import all models to register them
    from database.models import user, category, transaction, wallet, budget, debt, goal, credit, recurring, family

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database engine."""
    await engine.dispose()
