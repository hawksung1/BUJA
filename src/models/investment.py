"""
투자 관련 모델
"""
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class InvestmentPreference(Base, TimestampMixin):
    """투자 성향 모델"""

    __tablename__ = "investment_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    risk_tolerance: Mapped[int] = mapped_column(nullable=False)  # 1-10 scale
    target_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    investment_period: Mapped[Optional[str]] = mapped_column(String(20))  # SHORT, MEDIUM, LONG
    preferred_asset_types: Mapped[Optional[list[str]]] = mapped_column(JSON)  # SQLite 호환: JSON으로 저장
    max_loss_tolerance: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))  # percentage
    investment_experience: Mapped[Optional[str]] = mapped_column(String(20))  # BEGINNER, INTERMEDIATE, ADVANCED
    # 글로벌 포트폴리오 관련
    preferred_regions: Mapped[Optional[list[str]]] = mapped_column(JSON)  # 선호 투자 지역 (예: ["KOREA", "USA", "EUROPE", "ASIA"])
    currency_hedge_preference: Mapped[Optional[str]] = mapped_column(String(20))  # 환율 헷지 선호도 (NONE, PARTIAL, FULL)
    home_country: Mapped[Optional[str]] = mapped_column(String(50))  # 거주 국가 (기본 통화 기준)

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="investment_preference")

    def __repr__(self) -> str:
        return f"<InvestmentPreference(id={self.id}, user_id={self.user_id}, risk_tolerance={self.risk_tolerance})>"


class InvestmentRecord(Base, TimestampMixin):
    """투자 기록 모델"""

    __tablename__ = "investment_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(String(50))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    buy_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    sell_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    buy_date: Mapped[date] = mapped_column(Date, nullable=False)
    sell_date: Mapped[Optional[date]] = mapped_column(Date)
    fees: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    taxes: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    dividend_interest: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    profit_loss: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    realized: Mapped[bool] = mapped_column(default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="investment_records")

    def __repr__(self) -> str:
        return f"<InvestmentRecord(id={self.id}, user_id={self.user_id}, asset_type={self.asset_type})>"

