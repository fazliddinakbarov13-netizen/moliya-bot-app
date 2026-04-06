"""Credit model for loan tracking and calculation."""

from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, Float, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class Credit(Base, TimestampMixin):
    """Credit/loan model."""

    __tablename__ = "credits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    principal: Mapped[float] = mapped_column(Float)  # Asosiy summa
    annual_rate: Mapped[float] = mapped_column(Float)  # Yillik foiz
    term_months: Mapped[int] = mapped_column(Integer)  # Muddat (oyda)
    payment_type: Mapped[str] = mapped_column(String(20), default="annuity")
    # "annuity" or "differential"
    monthly_payment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="credits")

    def calculate_annuity_payment(self) -> float:
        """Calculate monthly annuity payment."""
        r = self.annual_rate / 100 / 12  # Monthly rate
        n = self.term_months
        if r == 0:
            return self.principal / n
        payment = self.principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return round(payment, 2)

    def calculate_total_payment(self) -> float:
        """Calculate total payment over the loan term."""
        if self.payment_type == "annuity":
            return self.calculate_annuity_payment() * self.term_months
        else:
            # Differential — approximate
            r = self.annual_rate / 100 / 12
            principal_part = self.principal / self.term_months
            total = 0
            remaining = self.principal
            for _ in range(self.term_months):
                interest = remaining * r
                total += principal_part + interest
                remaining -= principal_part
            return round(total, 2)

    def calculate_overpayment(self) -> float:
        """Calculate total overpayment (interest only)."""
        return round(self.calculate_total_payment() - self.principal, 2)

    def __repr__(self) -> str:
        return f"<Credit(id={self.id}, name={self.name}, principal={self.principal})>"
