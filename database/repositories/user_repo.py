"""User repository for user-related database operations."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User
from database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        telegram_id: int,
        first_name: str,
        username: Optional[str] = None,
        language: str = "uz",
    ) -> User:
        """Create a new user."""
        return await self.create(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
            language=language,
        )

    async def update_user(self, telegram_id: int, **kwargs) -> Optional[User]:
        """Update user by Telegram ID."""
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def get_all_users_with_reminders(self):
        """Get all users with enabled reminders."""
        result = await self.session.execute(
            select(User).where(
                User.reminder_enabled == True,
                User.is_onboarded == True,
            )
        )
        return result.scalars().all()

    async def set_onboarded(self, telegram_id: int) -> Optional[User]:
        """Mark user as onboarded."""
        return await self.update_user(telegram_id, is_onboarded=True)
