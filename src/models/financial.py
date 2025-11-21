"""
재무 관련 모델
"""
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class FinancialSituation(Base, TimestampMixin):
    """재무 상황 모델"""

    __tablename__ = "financial_situations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    monthly_income: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    monthly_expense: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    total_assets: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    total_debt: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    emergency_fund: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    family_members: Mapped[Optional[int]] = mapped_column(Integer)
    insurance_coverage: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="financial_situation")

    def __repr__(self) -> str:
        return f"<FinancialSituation(id={self.id}, user_id={self.user_id})>"


class FinancialGoal(Base, TimestampMixin):
    """재무 목표 모델"""

    __tablename__ = "financial_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    goal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False)
    current_progress: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="financial_goals")

    def __repr__(self) -> str:
        return f"<FinancialGoal(id={self.id}, user_id={self.user_id}, goal_type={self.goal_type})>"

