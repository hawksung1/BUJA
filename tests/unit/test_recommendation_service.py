"""
RecommendationService 단위 테스트
"""
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.recommendation_service import RecommendationService
from src.models import InvestmentPreference, FinancialSituation, AssetRecommendation
from config.database import Database


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def recommendation_service(mock_db):
    """RecommendationService 인스턴스"""
    service = RecommendationService(database=mock_db)
    return service


class TestRecommendationService:
    """RecommendationService 테스트"""
    
    @pytest.mark.asyncio
    async def test_generate_initial_recommendation(
        self, recommendation_service, mock_db
    ):
        """최초 자산 구성 추천 생성 테스트"""
        # Mock 설정
        preference = InvestmentPreference(
            id=1,
            user_id=1,
            risk_tolerance=5,
            target_return=Decimal("8.0"),
            preferred_asset_types=["STOCK", "BOND"]
        )
        
        financial = FinancialSituation(
            id=1,
            user_id=1,
            total_assets=Decimal("10000000")
        )
        
        mock_preference_repo = MagicMock()
        mock_preference_repo.get_by_user_id = AsyncMock(return_value=preference)
        recommendation_service.preference_repo = mock_preference_repo
        
        mock_financial_repo = MagicMock()
        mock_financial_repo.get_by_user_id = AsyncMock(return_value=financial)
        recommendation_service.financial_repo = mock_financial_repo
        
        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        recommendation_service.user_service = mock_user_service
        
        mock_recommendation_repo = MagicMock()
        mock_recommendation_repo.create = AsyncMock(return_value=AssetRecommendation(
            id=1, user_id=1, recommendation_type="INITIAL"
        ))
        recommendation_service.recommendation_repo = mock_recommendation_repo
        
        mock_session = AsyncMock()
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Agent mock
        recommendation_service.agent.chat = AsyncMock(return_value="추천 근거")
        
        result = await recommendation_service.generate_initial_recommendation(1)
        
        assert result.recommendation_type == "INITIAL"
        mock_preference_repo.get_by_user_id.assert_called_once_with(1)
        mock_financial_repo.get_by_user_id.assert_called_once_with(1)

