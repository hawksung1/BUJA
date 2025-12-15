"""
InvestmentPreferenceService 단위 테스트
"""
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from config.database import Database
from src.models import InvestmentPreference
from src.repositories import InvestmentPreferenceRepository
from src.services.investment_preference_service import InvestmentPreferenceService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def investment_preference_service(mock_db):
    """InvestmentPreferenceService 인스턴스"""
    return InvestmentPreferenceService(database=mock_db)


class TestInvestmentPreferenceService:
    """InvestmentPreferenceService 테스트"""

    @pytest.mark.asyncio
    async def test_calculate_risk_tolerance_from_survey(self, investment_preference_service):
        """설문조사 기반 위험 감수 성향 계산 테스트"""
        survey_answers = {
            "investment_experience": "ADVANCED",
            "investment_period": "LONG",
            "loss_tolerance": 4,
            "return_expectation": 5,
            "volatility_comfort": 4
        }

        risk_tolerance = await investment_preference_service.calculate_risk_tolerance_from_survey(
            survey_answers
        )

        assert 1 <= risk_tolerance <= 10
        assert risk_tolerance >= 7  # ADVANCED + LONG이면 높은 점수

    @pytest.mark.asyncio
    async def test_calculate_risk_tolerance_conservative(self, investment_preference_service):
        """보수적 투자 성향 계산 테스트"""
        survey_answers = {
            "investment_experience": "BEGINNER",
            "investment_period": "SHORT",
            "loss_tolerance": 1,
            "return_expectation": 2,
            "volatility_comfort": 1
        }

        risk_tolerance = await investment_preference_service.calculate_risk_tolerance_from_survey(
            survey_answers
        )

        assert risk_tolerance <= 5  # 보수적이면 낮은 점수

    @pytest.mark.asyncio
    async def test_generate_preference_report(self, investment_preference_service, mock_db):
        """투자 성향 분석 리포트 생성 테스트"""
        preference = InvestmentPreference(
            id=1,
            user_id=1,
            risk_tolerance=7,
            target_return=Decimal("10.0"),
            investment_period="LONG",
            updated_at=datetime.now()
        )

        mock_preference_repo = MagicMock(spec=InvestmentPreferenceRepository)
        mock_preference_repo.get_by_user_id = AsyncMock(return_value=preference)
        investment_preference_service.preference_repo = mock_preference_repo

        report = await investment_preference_service.generate_preference_report(1)

        assert report["risk_tolerance"] == 7
        assert report["risk_level"] in ["보수적", "중립", "공격적"]
        assert "recommended_allocation" in report
        assert "주식" in report["recommended_allocation"]

