"""Category model."""

from sqlalchemy import BigInteger, Boolean, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class Category(Base):
    """Expense/income category model."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    name_uz: Mapped[str] = mapped_column(String(100))
    name_ru: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(10), default="📦")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, icon={self.icon})>"
