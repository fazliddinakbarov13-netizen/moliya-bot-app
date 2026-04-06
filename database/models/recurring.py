"""Recurring expense model for automatic monthly entries."""

from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, Float, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class RecurringExpense(Base):
    """Recurring monthly expense model."""

    __tablename__ = "recurring_expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    wallet_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("wallets.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(Float)
    day_of_month: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_executed: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    user = relationship("User", back_populates="recurring_expenses")

    def __repr__(self) -> str:
        return f"<RecurringExpense(id={self.id}, name={self.name}, amount={self.amount})>"
