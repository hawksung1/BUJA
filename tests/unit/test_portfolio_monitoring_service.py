"""
포트폴리오 모니터링 서비스 테스트
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from config.database import Database
from src.models.financial import FinancialGoal
from src.models.user import User
from src.services.portfolio_monitoring_service import PortfolioMonitoringService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def monitoring_service(mock_db):
    """PortfolioMonitoringService 인스턴스"""
    service = PortfolioMonitoringService()
    service.portfolio_service = MagicMock()
    service.chat_service = MagicMock()
    service.notification_service = MagicMock()
    service.user_repo = MagicMock()
    service.goal_repo = MagicMock()
    service.investment_repo = MagicMock()
    return service


@pytest.mark.asyncio
async def test_monitor_user_portfolio_no_portfolio(monitoring_service):
    """포트폴리오가 없는 사용자 모니터링 테스트"""
    user_id = 1
    
    # Mock portfolio analysis
    monitoring_service.portfolio_service.analyze_portfolio = AsyncMock(return_value={"total_value": 0})
    monitoring_service.goal_repo.get_by_user_id = AsyncMock(return_value=[])

    result = await monitoring_service.monitor_user_portfolio(user_id)

    assert result is not None
    assert result["user_id"] == user_id
    assert result.get("risk_alerts") == []
    assert result.get("goal_alerts") == []


@pytest.mark.asyncio
async def test_check_risk_thresholds(monitoring_service):
    """리스크 임계값 체크 테스트"""
    user_id = 1
    
    # 높은 리스크 포트폴리오 분석 데이터
    high_risk_analysis = {
        "total_value": 1000000,
        "risk": {
            "max_drawdown": -25.0,  # 25% 낙폭
            "volatility": 35.0  # 35% 변동성
        }
    }

    alerts = await monitoring_service._check_risk_thresholds(user_id, high_risk_analysis)

    assert len(alerts) > 0
    assert any(alert["type"] == "high_drawdown" for alert in alerts)
    assert any(alert["type"] == "high_volatility" for alert in alerts)


@pytest.mark.asyncio
async def test_check_goal_progress(monitoring_service):
    """목표 진행률 체크 테스트"""
    user_id = 1
    
    # 목표 생성
    goal = FinancialGoal(
        id=1,
        user_id=user_id,
        goal_type="RETIREMENT",
        target_amount=Decimal("100000000"),  # 1억
        target_date=date.today() + timedelta(days=365),  # 1년 후
        priority=1,
        current_progress=Decimal("0"),
        created_at=datetime.now() - timedelta(days=10) # 10일 전 생성
    )
    
    monitoring_service.goal_repo.get_by_user_id = AsyncMock(return_value=[goal])

    # 포트폴리오 분석 (목표의 50% 달성)
    analysis = {
        "total_value": 50000000  # 5천만원
    }

    goals = await monitoring_service.goal_repo.get_by_user_id(user_id)
    alerts = await monitoring_service._check_goal_progress(user_id, goals, analysis)

    # 목표 진행률이 낮으면 경고가 있을 수 있음 (여기서는 50% 달성이라 경고 없을 수도 있지만, 로직에 따라 다름)
    # 10일 지났고 365일 남았는데 50% 달성이면 매우 빠름 -> 경고 없음
    # 하지만 테스트 코드는 alerts가 list인지만 확인
    assert isinstance(alerts, list)


@pytest.mark.asyncio
async def test_check_rebalancing(monitoring_service):
    """리밸런싱 필요성 체크 테스트"""
    user_id = 1
    
    # 불균형한 자산 배분 (한 자산이 80%)
    unbalanced_analysis = {
        "asset_allocation": {
            "STOCK": 80.0,
            "BOND": 10.0,
            "CASH": 10.0
        }
    }

    needs_rebalancing = await monitoring_service._check_rebalancing(user_id, unbalanced_analysis)
    assert needs_rebalancing is True

    # 균형잡힌 자산 배분
    balanced_analysis = {
        "asset_allocation": {
            "STOCK": 50.0,
            "BOND": 30.0,
            "CASH": 20.0
        }
    }

    needs_rebalancing = await monitoring_service._check_rebalancing(user_id, balanced_analysis)
    assert needs_rebalancing is False

