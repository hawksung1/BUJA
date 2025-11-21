"""
Repository 패턴 구현
"""
from src.repositories.base_repository import BaseRepository
from src.repositories.chat_project_repository import ChatProjectRepository
from src.repositories.chat_repository import ChatMessageRepository
from src.repositories.investment_repository import (
    FinancialGoalRepository,
    FinancialSituationRepository,
    InvestmentPreferenceRepository,
    InvestmentRecordRepository,
)
from src.repositories.portfolio_repository import (
    AssetRecommendationRepository,
    PortfolioAnalysisRepository,
    RebalancingHistoryRepository,
    ScreenshotRepository,
)
from src.repositories.user_repository import (
    UserProfileRepository,
    UserRepository,
)
from src.repositories.notification_repository import NotificationRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "UserProfileRepository",
    "ScreenshotRepository",
    "PortfolioAnalysisRepository",
    "AssetRecommendationRepository",
    "RebalancingHistoryRepository",
    "InvestmentPreferenceRepository",
    "InvestmentRecordRepository",
    "FinancialSituationRepository",
    "FinancialGoalRepository",
    "ChatMessageRepository",
    "ChatProjectRepository",
    "NotificationRepository",
]

