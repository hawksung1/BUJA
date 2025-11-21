"""
포트폴리오 모니터링 서비스 테스트
"""
from decimal import Decimal

import pytest

from src.models.user import User
from src.services.portfolio_monitoring_service import PortfolioMonitoringService
from src.utils.security import hash_password


@pytest.mark.asyncio
async def test_monitor_user_portfolio_no_portfolio(db_session):
    """포트폴리오가 없는 사용자 모니터링 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_monitor@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = PortfolioMonitoringService()

    result = await service.monitor_user_portfolio(user.id)

    assert result is not None
    assert result["user_id"] == user.id
    # 포트폴리오가 없으면 알림 없음
    assert result.get("risk_alerts") == []
    assert result.get("goal_alerts") == []


@pytest.mark.asyncio
async def test_check_risk_thresholds(db_session):
    """리스크 임계값 체크 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_risk@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = PortfolioMonitoringService()

    # 높은 리스크 포트폴리오 분석 데이터
    high_risk_analysis = {
        "total_value": 1000000,
        "risk": {
            "max_drawdown": -25.0,  # 25% 낙폭
            "volatility": 35.0  # 35% 변동성
        }
    }

    alerts = await service._check_risk_thresholds(user.id, high_risk_analysis)

    assert len(alerts) > 0
    assert any(alert["type"] == "high_drawdown" for alert in alerts)


@pytest.mark.asyncio
async def test_check_goal_progress(db_session):
    """목표 진행률 체크 테스트"""
    from datetime import date, timedelta

    from src.models.financial import FinancialGoal

    # 테스트 사용자 생성
    user = User(
        email="test_goal@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = PortfolioMonitoringService()

    # 목표 생성
    goal = FinancialGoal(
        user_id=user.id,
        goal_type="RETIREMENT",
        target_amount=Decimal("100000000"),  # 1억
        target_date=date.today() + timedelta(days=365),  # 1년 후
        priority=1,
        current_progress=Decimal("0")
    )
    await service.goal_repo.create(goal)

    # 포트폴리오 분석 (목표의 50% 달성)
    analysis = {
        "total_value": 50000000  # 5천만원
    }

    goals = await service.goal_repo.get_by_user_id(user.id)
    alerts = await service._check_goal_progress(user.id, goals, analysis)

    # 목표 진행률이 낮으면 경고가 있을 수 있음
    assert isinstance(alerts, list)


@pytest.mark.asyncio
async def test_check_rebalancing(db_session):
    """리밸런싱 필요성 체크 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_rebalancing@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = PortfolioMonitoringService()

    # 불균형한 자산 배분 (한 자산이 80%)
    unbalanced_analysis = {
        "asset_allocation": {
            "STOCK": 80.0,
            "BOND": 10.0,
            "CASH": 10.0
        }
    }

    needs_rebalancing = await service._check_rebalancing(user.id, unbalanced_analysis)
    assert needs_rebalancing is True

    # 균형잡힌 자산 배분
    balanced_analysis = {
        "asset_allocation": {
            "STOCK": 50.0,
            "BOND": 30.0,
            "CASH": 20.0
        }
    }

    needs_rebalancing = await service._check_rebalancing(user.id, balanced_analysis)
    assert needs_rebalancing is False

