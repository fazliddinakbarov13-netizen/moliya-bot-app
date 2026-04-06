"""Budget repository for spending limits and monitoring."""

from typing import Optional, Sequence
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.budget import Budget
from database.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    """Repository for Budget model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Budget)

    async def get_overall_budget(
        self, user_id: int, month: int, year: int
    ) -> Optional[Budget]:
        """Get overall monthly budget."""
        result = await self.session.execute(
            select(Budget).where(
                and_(
                    Budget.user_id == user_id,
                    Budget.category_id == None,
                    Budget.month == month,
                    Budget.year == year,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_category_budget(
        self, user_id: int, category_id: int, month: int, year: int
    ) -> Optional[Budget]:
        """Get budget for a specific category."""
        result = await self.session.execute(
            select(Budget).where(
                and_(
                    Budget.user_id == user_id,
                    Budget.category_id == category_id,
                    Budget.month == month,
                    Budget.year == year,
                )
            )
        )
        return result.scalar_one_or_none()

    async def set_overall_budget(
        self, user_id: int, amount: float, month: int, year: int
    ) -> Budget:
        """Set or update overall monthly budget."""
        budget = await self.get_overall_budget(user_id, month, year)
        if budget:
            budget.amount = amount
            await self.session.commit()
            await self.session.refresh(budget)
            return budget
        return await self.create(
            user_id=user_id,
            amount=amount,
            month=month,
            year=year,
            category_id=None,
        )

    async def set_category_budget(
        self, user_id: int, category_id: int, amount: float, month: int, year: int
    ) -> Budget:
        """Set or update budget for a specific category."""
        budget = await self.get_category_budget(user_id, category_id, month, year)
        if budget:
            budget.amount = amount
            await self.session.commit()
            await self.session.refresh(budget)
            return budget
        return await self.create(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            month=month,
            year=year,
        )

    async def get_all_budgets(
        self, user_id: int, month: int, year: int
    ) -> Sequence[Budget]:
        """Get all budgets for a user in a given month."""
        result = await self.session.execute(
            select(Budget).where(
                and_(
                    Budget.user_id == user_id,
                    Budget.month == month,
                    Budget.year == year,
                )
            )
        )
        return result.scalars().all()
