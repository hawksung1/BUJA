"""
목표 추적 서비스 테스트
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.models.financial import FinancialGoal
from src.models.user import User
from src.services.goal_tracking_service import GoalTrackingService
from src.utils.security import hash_password


@pytest.mark.asyncio
async def test_calculate_goal_progress(db_session):
    """목표 진행률 계산 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_goal_progress@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = GoalTrackingService()

    # 목표 생성
    goal = FinancialGoal(
        user_id=user.id,
        goal_type="HOUSE",
        target_amount=Decimal("500000000"),  # 5억
        target_date=date.today() + timedelta(days=365),
        priority=1,
        current_progress=Decimal("0")
    )
    await service.goal_repo.create(goal)

    # 진행률 계산
    result = await service.calculate_goal_progress(user.id)

    assert result is not None
    assert result["user_id"] == user.id
    assert "goals" in result
    assert len(result["goals"]) > 0


@pytest.mark.asyncio
async def test_predict_goal_achievement(db_session):
    """목표 달성 예측 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_predict@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = GoalTrackingService()

    # 목표 생성
    goal = FinancialGoal(
        user_id=user.id,
        goal_type="EDUCATION",
        target_amount=Decimal("100000000"),  # 1억
        target_date=date.today() + timedelta(days=730),  # 2년 후
        priority=1,
        current_progress=Decimal("0")
    )
    await service.goal_repo.create(goal)

    # 예측
    result = await service.predict_goal_achievement(user.id, goal.id)

    assert result is not None
    assert "achievement_probability" in result
    assert 0 <= result["achievement_probability"] <= 1


@pytest.mark.asyncio
async def test_assess_goal_risk(db_session):
    """목표 달성 위험도 평가 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_risk_assess@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = GoalTrackingService()

    # 목표 생성
    goal = FinancialGoal(
        user_id=user.id,
        goal_type="RETIREMENT",
        target_amount=Decimal("1000000000"),  # 10억
        target_date=date.today() + timedelta(days=365),
        priority=1,
        current_progress=Decimal("0")
    )
    await service.goal_repo.create(goal)

    # 위험도 평가
    result = await service.assess_goal_risk(user.id, goal.id)

    assert result is not None
    assert "risk_score" in result
    assert "risk_level" in result
    assert result["risk_level"] in ["low", "medium", "high"]

