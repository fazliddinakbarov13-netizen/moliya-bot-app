"""Transaction repository for expense/income operations."""

from datetime import date, datetime
from typing import Optional, Sequence
from sqlalchemy import select, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.transaction import Transaction
from database.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)

    async def add_expense(
        self,
        user_id: int,
        amount: float,
        category_id: int,
        description: str = "",
        transaction_date: date = None,
        wallet_id: int = None,
        source: str = "manual",
    ) -> Transaction:
        """Add a new expense transaction."""
        return await self.create(
            user_id=user_id,
            type="expense",
            amount=amount,
            category_id=category_id,
            description=description,
            transaction_date=transaction_date or date.today(),
            wallet_id=wallet_id,
            source=source,
        )

    async def add_income(
        self,
        user_id: int,
        amount: float,
        income_type: str = "salary",
        description: str = "",
        transaction_date: date = None,
        wallet_id: int = None,
    ) -> Transaction:
        """Add a new income transaction."""
        return await self.create(
            user_id=user_id,
            type="income",
            amount=amount,
            income_type=income_type,
            description=description,
            transaction_date=transaction_date or date.today(),
            wallet_id=wallet_id,
        )

    async def get_monthly_expenses(
        self, user_id: int, month: int, year: int
    ) -> Sequence[Transaction]:
        """Get all expenses for a specific month."""
        result = await self.session.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    extract("month", Transaction.transaction_date) == month,
                    extract("year", Transaction.transaction_date) == year,
                )
            ).order_by(Transaction.transaction_date.desc())
        )
        return result.scalars().all()

    async def get_monthly_income(
        self, user_id: int, month: int, year: int
    ) -> Sequence[Transaction]:
        """Get all income for a specific month."""
        result = await self.session.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == "income",
                    extract("month", Transaction.transaction_date) == month,
                    extract("year", Transaction.transaction_date) == year,
                )
            ).order_by(Transaction.transaction_date.desc())
        )
        return result.scalars().all()

    async def get_monthly_expense_total(
        self, user_id: int, month: int, year: int
    ) -> float:
        """Get total expenses for a month."""
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    extract("month", Transaction.transaction_date) == month,
                    extract("year", Transaction.transaction_date) == year,
                )
            )
        )
        return result.scalar() or 0.0

    async def get_monthly_income_total(
        self, user_id: int, month: int, year: int
    ) -> float:
        """Get total income for a month."""
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == "income",
                    extract("month", Transaction.transaction_date) == month,
                    extract("year", Transaction.transaction_date) == year,
                )
            )
        )
        return result.scalar() or 0.0

    async def get_expenses_by_category(
        self, user_id: int, month: int, year: int
    ) -> list[dict]:
        """Get expense totals grouped by category for a month."""
        from database.models.category import Category

        result = await self.session.execute(
            select(
                Category.name,
                Category.icon,
                func.sum(Transaction.amount).label("total"),
                func.count(Transaction.id).label("count"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    extract("month", Transaction.transaction_date) == month,
                    extract("year", Transaction.transaction_date) == year,
                )
            )
            .group_by(Category.name, Category.icon)
            .order_by(func.sum(Transaction.amount).desc())
        )
        rows = result.all()
        return [
            {"name": r.name, "icon": r.icon, "total": r.total, "count": r.count}
            for r in rows
        ]

    async def get_daily_expenses(
        self, user_id: int, target_date: date
    ) -> Sequence[Transaction]:
        """Get all expenses for a specific date."""
        result = await self.session.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    Transaction.transaction_date == target_date,
                )
            ).order_by(Transaction.created_at.desc())
        )
        return result.scalars().all()

    async def get_category_total_for_month(
        self, user_id: int, category_id: int, month: int, year: int
    ) -> float:
        """Get total expense in a specific category for a month."""
        result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    Transaction.category_id == category_id,
                    extract("month", Transaction.transaction_date) == month,
                    extract("year", Transaction.transaction_date) == year,
                )
            )
        )
        return result.scalar() or 0.0
