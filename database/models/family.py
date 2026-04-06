"""Family member model for shared household tracking."""

from datetime import datetime

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base, TimestampMixin


class FamilyMember(Base, TimestampMixin):
    """Family member linked to a primary user account."""

    __tablename__ = "family_members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    member_telegram_id: Mapped[int] = mapped_column(BigInteger)
    member_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default="spouse")

    def __repr__(self) -> str:
        return f"<FamilyMember(id={self.id}, name={self.member_name}, role={self.role})>"
