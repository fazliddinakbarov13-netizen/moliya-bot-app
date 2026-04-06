"""Transaction model for expenses and income."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, String, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    """Financial transaction (expense or income)."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    wallet_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("wallets.id"), nullable=True)

    # Transaction details
    type: Mapped[str] = mapped_column(String(20))  # "expense" or "income"
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, default=date.today)

    # Income subtype
    income_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # "salary", "salary_2", "additional", "other"

    # Source of entry
    source: Mapped[str] = mapped_column(String(20), default="manual")
    # "manual", "voice", "photo", "auto"

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, type={self.type}, amount={self.amount})>"
