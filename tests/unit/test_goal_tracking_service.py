"""
목표 추적 서비스 테스트
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from config.database import Database
from src.models.financial import FinancialGoal
from src.services.goal_tracking_service import GoalTrackingService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def goal_tracking_service(mock_db):
    """GoalTrackingService 인스턴스"""
    service = GoalTrackingService()
    # Mocking internal repositories/services
    service.goal_repo = MagicMock()
    service.portfolio_service = MagicMock()
    service.portfolio_service.analyze_portfolio = AsyncMock(return_value={"total_value": Decimal("100000000")})
    service.investment_repo = MagicMock()
    return service


@pytest.mark.asyncio
async def test_calculate_goal_progress(goal_tracking_service):
    """목표 진행률 계산 테스트"""
    user_id = 1
    
    # Mock goals
    goals = [
        FinancialGoal(
            id=1, user_id=user_id, goal_type="HOUSE",
            target_amount=Decimal("500000000"),
            target_date=date.today() + timedelta(days=365),
            current_progress=Decimal("100000000"),
            created_at=datetime.now()
        )
    ]
    
    # Mock repository
    mock_goal_repo = MagicMock()
    mock_goal_repo.get_by_user_id = AsyncMock(return_value=goals)
    goal_tracking_service.goal_repo = mock_goal_repo
    
    # Mock portfolio service for current assets
    mock_portfolio_service = MagicMock()
    mock_portfolio_service.analyze_portfolio = AsyncMock(return_value={"total_value": Decimal("150000000")})
    goal_tracking_service.portfolio_service = mock_portfolio_service

    # 진행률 계산
    result = await goal_tracking_service.calculate_goal_progress(user_id)

    assert result is not None
    assert result["user_id"] == user_id
    assert "goals" in result
    assert len(result["goals"]) == 1
    assert result["goals"][0]["progress_ratio"] > 0


@pytest.mark.asyncio
async def test_predict_goal_achievement(goal_tracking_service):
    """목표 달성 예측 테스트"""
    user_id = 1
    goal_id = 1
    
    goal = FinancialGoal(
        id=goal_id, user_id=user_id, goal_type="EDUCATION",
        target_amount=Decimal("100000000"),
        target_date=date.today() + timedelta(days=730),
        current_progress=Decimal("20000000"),
        created_at=datetime.now()
    )
    
    mock_goal_repo = MagicMock()
    mock_goal_repo.get_by_id = AsyncMock(return_value=goal)
    goal_tracking_service.goal_repo = mock_goal_repo
    
    # Mock prediction logic dependencies if any
    # Assuming the service uses some internal logic or external service for prediction
    # For now, we test if it runs without error and returns expected structure
    
    result = await goal_tracking_service.predict_goal_achievement(user_id, goal_id)

    assert result is not None
    assert "achievement_probability" in result
    # Probability should be between 0 and 1 (or 0 and 100 depending on implementation)
    # Adjust assertion based on actual implementation details
    assert result["achievement_probability"] >= 0


@pytest.mark.asyncio
async def test_assess_goal_risk(goal_tracking_service):
    """목표 달성 위험도 평가 테스트"""
    user_id = 1
    goal_id = 1
    
    goal = FinancialGoal(
        id=goal_id, user_id=user_id, goal_type="RETIREMENT",
        target_amount=Decimal("1000000000"),
        target_date=date.today() + timedelta(days=365),
        current_progress=Decimal("10000000"),
        created_at=datetime.now()
    )
    
    mock_goal_repo = MagicMock()
    mock_goal_repo.get_by_id = AsyncMock(return_value=goal)
    goal_tracking_service.goal_repo = mock_goal_repo

    result = await goal_tracking_service.assess_goal_risk(user_id, goal_id)

    assert result is not None
    assert "risk_score" in result
    assert "risk_level" in result
    assert result["risk_level"] in ["low", "medium", "high", "critical"]

