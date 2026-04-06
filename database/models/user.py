"""User model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Telegram user model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Settings
    language: Mapped[str] = mapped_column(String(5), default="uz")
    currency: Mapped[str] = mapped_column(String(5), default="UZS")
    family_status: Mapped[str] = mapped_column(String(20), default="single")

    # Security
    pin_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Premium
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Monthly income
    monthly_income: Mapped[Optional[float]] = mapped_column(default=0.0)
    monthly_income_2: Mapped[Optional[float]] = mapped_column(default=0.0)  # spouse

    # Reminder
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    reminder_hour: Mapped[int] = mapped_column(Integer, default=21)
    reminder_minute: Mapped[int] = mapped_column(Integer, default=0)

    # Onboarding
    is_onboarded: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships — lazy="noload" prevents N+1 queries, load explicitly when needed
    categories = relationship("Category", back_populates="user", lazy="noload")
    transactions = relationship("Transaction", back_populates="user", lazy="noload")
    wallets = relationship("Wallet", back_populates="user", lazy="noload")
    budgets = relationship("Budget", back_populates="user", lazy="noload")
    debts = relationship("Debt", back_populates="user", lazy="noload")
    goals = relationship("Goal", back_populates="user", lazy="noload")
    credits = relationship("Credit", back_populates="user", lazy="noload")
    recurring_expenses = relationship("RecurringExpense", back_populates="user", lazy="noload")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.first_name})>"
