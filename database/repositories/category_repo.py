"""Category repository for managing user categories."""

from typing import Optional, Sequence
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.category import Category
from database.repositories.base import BaseRepository
from bot.utils.constants import DEFAULT_CATEGORIES


class CategoryRepository(BaseRepository[Category]):
    """Repository for Category model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    async def get_user_categories(
        self, user_id: int, active_only: bool = True
    ) -> Sequence[Category]:
        """Get all categories for a user."""
        query = select(Category).where(Category.user_id == user_id)
        if active_only:
            query = query.where(Category.is_active == True)
        query = query.order_by(Category.sort_order)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_category_count(self, user_id: int) -> int:
        """Get count of active categories for a user."""
        result = await self.session.execute(
            select(func.count(Category.id)).where(
                and_(Category.user_id == user_id, Category.is_active == True)
            )
        )
        return result.scalar() or 0

    async def create_default_categories(self, user_id: int) -> list[Category]:
        """Create default categories for a new user."""
        categories = []
        for i, cat in enumerate(DEFAULT_CATEGORIES):
            category = Category(
                user_id=user_id,
                name=cat["name"],
                name_uz=cat["name_uz"],
                name_ru=cat["name_ru"],
                icon=cat["icon"],
                sort_order=i,
                is_default=True,
                is_active=True,
            )
            self.session.add(category)
            categories.append(category)
        await self.session.commit()
        return categories

    async def add_category(
        self,
        user_id: int,
        name: str,
        icon: str = "📦",
        name_uz: str = "",
        name_ru: str = "",
    ) -> Optional[Category]:
        """Add a custom category for a user."""
        count = await self.get_user_category_count(user_id)
        if count >= 20:
            return None  # Max limit reached

        sort_order = count
        return await self.create(
            user_id=user_id,
            name=name,
            name_uz=name_uz or name,
            name_ru=name_ru or name,
            icon=icon,
            sort_order=sort_order,
            is_default=False,
        )

    async def rename_category(
        self, category_id: int, new_name: str
    ) -> Optional[Category]:
        """Rename a category."""
        return await self.update_by_id(
            category_id, name=new_name, name_uz=new_name, name_ru=new_name
        )

    async def change_icon(
        self, category_id: int, new_icon: str
    ) -> Optional[Category]:
        """Change category icon."""
        return await self.update_by_id(category_id, icon=new_icon)

    async def deactivate_category(self, category_id: int) -> Optional[Category]:
        """Soft delete a category (keep data)."""
        return await self.update_by_id(category_id, is_active=False)

    async def find_by_name(
        self, user_id: int, name: str
    ) -> Optional[Category]:
        """Find a category by name (case-insensitive)."""
        result = await self.session.execute(
            select(Category).where(
                and_(
                    Category.user_id == user_id,
                    func.lower(Category.name) == name.lower(),
                    Category.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def reset_to_defaults(self, user_id: int) -> list[Category]:
        """Deactivate all current categories and create defaults."""
        # Deactivate all
        categories = await self.get_user_categories(user_id)
        for cat in categories:
            cat.is_active = False
        await self.session.commit()

        # Create new defaults
        return await self.create_default_categories(user_id)
