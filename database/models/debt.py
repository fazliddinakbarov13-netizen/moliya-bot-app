"""Debt model for tracking money lent/borrowed."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class Debt(Base, TimestampMixin):
    """Debt tracking model."""

    __tablename__ = "debts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    person_name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(10))  # "gave" or "took"
    original_amount: Mapped[float] = mapped_column(Float)
    remaining_amount: Mapped[float] = mapped_column(Float)
    note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_settled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="debts")

    def __repr__(self) -> str:
        return f"<Debt(id={self.id}, person={self.person_name}, remaining={self.remaining_amount})>"
