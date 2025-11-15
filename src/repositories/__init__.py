"""
Repository 패턴 구현
"""
from src.repositories.base_repository import BaseRepository
from src.repositories.user_repository import (
    UserRepository,
    UserProfileRepository,
)
from src.repositories.portfolio_repository import (
    ScreenshotRepository,
    PortfolioAnalysisRepository,
    AssetRecommendationRepository,
    RebalancingHistoryRepository,
)
from src.repositories.investment_repository import (
    InvestmentPreferenceRepository,
    InvestmentRecordRepository,
    FinancialSituationRepository,
    FinancialGoalRepository,
)
from src.repositories.chat_repository import ChatMessageRepository
from src.repositories.chat_project_repository import ChatProjectRepository

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
]

