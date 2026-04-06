"""Goal model for financial target tracking."""

from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class Goal(Base, TimestampMixin):
    """Financial goal model."""

    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    target_amount: Mapped[float] = mapped_column(Float)
    current_amount: Mapped[float] = mapped_column(Float, default=0.0)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    icon: Mapped[str] = mapped_column(String(10), default="🎯")
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="goals")

    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.target_amount <= 0:
            return 0.0
        return min(100.0, (self.current_amount / self.target_amount) * 100)

    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount."""
        return max(0.0, self.target_amount - self.current_amount)

    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, name={self.name}, progress={self.progress_percent:.1f}%)>"
