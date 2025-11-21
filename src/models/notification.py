"""
알림 모델
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class NotificationType(str, Enum):
    """알림 유형"""
    RISK_ALERT = "risk_alert"              # 리스크 경고
    GOAL_PROGRESS = "goal_progress"        # 목표 진행률
    REBALANCING_NEEDED = "rebalancing"     # 리밸런싱 필요
    PORTFOLIO_REVIEW = "portfolio_review"  # 포트폴리오 리뷰
    GOAL_AT_RISK = "goal_at_risk"         # 목표 달성 위험
    GOAL_NEAR_COMPLETION = "goal_near"     # 목표 달성 임박


class NotificationStatus(str, Enum):
    """알림 상태"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class Notification(Base, TimestampMixin):
    """알림 모델"""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus),
        default=NotificationStatus.UNREAD,
        nullable=False
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 메타데이터 (JSON 형태로 저장)
    # Note: 'metadata'는 SQLAlchemy 예약어이므로 컬럼명을 명시적으로 지정
    meta_data: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)  # JSON string
    
    # 관계
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"

