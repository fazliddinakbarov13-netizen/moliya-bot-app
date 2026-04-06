"""Wallet model for multi-account support."""

from sqlalchemy import BigInteger, Boolean, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class Wallet(Base):
    """User wallet/account model."""

    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20), default="cash")  # cash, card
    icon: Mapped[str] = mapped_column(String(10), default="💵")
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Wallet(id={self.id}, name={self.name}, balance={self.balance})>"
