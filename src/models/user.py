"""
사용자 관련 모델
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.financial import FinancialSituation, FinancialGoal
    from src.models.investment import InvestmentPreference, InvestmentRecord
    from src.models.portfolio import Screenshot, PortfolioAnalysis, AssetRecommendation
    from src.models.chat import ChatMessage
    from src.models.chat_project import ChatProject


class User(Base, TimestampMixin):
    """사용자 모델"""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # 관계
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    financial_situation: Mapped[Optional["FinancialSituation"]] = relationship(
        "FinancialSituation",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    investment_preference: Mapped[Optional["InvestmentPreference"]] = relationship(
        "InvestmentPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    financial_goals: Mapped[list["FinancialGoal"]] = relationship(
        "FinancialGoal",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    investment_records: Mapped[list["InvestmentRecord"]] = relationship(
        "InvestmentRecord",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    screenshots: Mapped[list["Screenshot"]] = relationship(
        "Screenshot",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    portfolio_analyses: Mapped[list["PortfolioAnalysis"]] = relationship(
        "PortfolioAnalysis",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    asset_recommendations: Mapped[list["AssetRecommendation"]] = relationship(
        "AssetRecommendation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )
    chat_projects: Mapped[list["ChatProject"]] = relationship(
        "ChatProject",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ChatProject.created_at"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class UserProfile(Base, TimestampMixin):
    """사용자 프로필 모델"""
    
    __tablename__ = "user_profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(100))
    age: Mapped[Optional[int]] = mapped_column()
    occupation: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 관계
    user: Mapped["User"] = relationship("User", back_populates="profile")
    
    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, name={self.name})>"

