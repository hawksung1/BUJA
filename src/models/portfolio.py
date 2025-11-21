"""
포트폴리오 관련 모델
"""
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    JSON,  # SQLite 호환: JSONB 대신 JSON 사용
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class Screenshot(Base, TimestampMixin):
    """스크린샷 모델"""

    __tablename__ = "screenshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    app_type: Mapped[Optional[str]] = mapped_column(String(50))  # KEYUM, NH, UPBIT, etc.
    extracted_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)  # SQLite 호환
    analysis_status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False
    )  # PENDING, PROCESSING, COMPLETED, FAILED
    deleted_at: Mapped[Optional[datetime]] = mapped_column()

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="screenshots")
    portfolio_analyses: Mapped[list["PortfolioAnalysis"]] = relationship(
        "PortfolioAnalysis",
        back_populates="screenshot",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Screenshot(id={self.id}, user_id={self.user_id}, app_type={self.app_type})>"


class PortfolioAnalysis(Base):
    """포트폴리오 분석 모델"""

    __tablename__ = "portfolio_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    screenshot_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("screenshots.id", ondelete="SET NULL")
    )
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    asset_allocation: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)  # SQLite 호환
    risk_level: Mapped[Optional[str]] = mapped_column(String(20))
    diversification_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    performance_metrics: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)  # SQLite 호환
    recommendations: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="portfolio_analyses")
    screenshot: Mapped[Optional["Screenshot"]] = relationship(
        "Screenshot",
        back_populates="portfolio_analyses"
    )

    def __repr__(self) -> str:
        return f"<PortfolioAnalysis(id={self.id}, user_id={self.user_id}, analysis_date={self.analysis_date})>"


class AssetRecommendation(Base):
    """자산 추천 모델"""

    __tablename__ = "asset_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    recommendation_type: Mapped[Optional[str]] = mapped_column(String(50))  # INITIAL, REBALANCE, GOAL_BASED
    target_allocation: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)  # SQLite 호환
    reasoning: Mapped[Optional[str]] = mapped_column(Text)
    risk_assessment: Mapped[Optional[str]] = mapped_column(Text)
    expected_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column()

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="asset_recommendations")
    rebalancing_history: Mapped[list["RebalancingHistory"]] = relationship(
        "RebalancingHistory",
        back_populates="recommendation",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AssetRecommendation(id={self.id}, user_id={self.user_id}, type={self.recommendation_type})>"


class RebalancingHistory(Base):
    """리밸런싱 이력 모델"""

    __tablename__ = "rebalancing_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    recommendation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("asset_recommendations.id", ondelete="SET NULL")
    )
    before_allocation: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)  # SQLite 호환
    after_allocation: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)  # SQLite 호환
    rebalancing_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    executed_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )

    # 관계
    recommendation: Mapped[Optional["AssetRecommendation"]] = relationship(
        "AssetRecommendation",
        back_populates="rebalancing_history"
    )

    def __repr__(self) -> str:
        return f"<RebalancingHistory(id={self.id}, user_id={self.user_id})>"

