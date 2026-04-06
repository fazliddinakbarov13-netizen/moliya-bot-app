"""Budget model for monthly spending limits."""

from sqlalchemy import BigInteger, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from database.models.base import Base


class Budget(Base):
    """Monthly budget and category limits."""

    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )  # NULL = overall budget
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    month: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)

    # Relationships
    user = relationship("User", back_populates="budgets")

    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, amount={self.amount}, {self.month}/{self.year})>"
