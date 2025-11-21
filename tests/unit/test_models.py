"""
모델 단위 테스트
"""
from datetime import date
from decimal import Decimal

from src.models import (
    FinancialGoal,
    FinancialSituation,
    InvestmentPreference,
    InvestmentRecord,
    User,
    UserProfile,
)


class TestUserModel:
    """User 모델 테스트"""

    def test_user_creation(self):
        """User 생성 테스트"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.is_active is True

    def test_user_repr(self):
        """User __repr__ 테스트"""
        user = User(id=1, email="test@example.com", password_hash="hash")
        assert "User" in repr(user)
        assert "1" in repr(user)
        assert "test@example.com" in repr(user)


class TestUserProfileModel:
    """UserProfile 모델 테스트"""

    def test_user_profile_creation(self):
        """UserProfile 생성 테스트"""
        profile = UserProfile(
            user_id=1,
            name="Test User",
            age=30,
            occupation="Developer"
        )
        assert profile.user_id == 1
        assert profile.name == "Test User"
        assert profile.age == 30


class TestFinancialSituationModel:
    """FinancialSituation 모델 테스트"""

    def test_financial_situation_creation(self):
        """FinancialSituation 생성 테스트"""
        situation = FinancialSituation(
            user_id=1,
            monthly_income=Decimal("5000000"),
            monthly_expense=Decimal("3000000"),
            total_assets=Decimal("100000000")
        )
        assert situation.user_id == 1
        assert situation.monthly_income == Decimal("5000000")
        assert situation.total_assets == Decimal("100000000")


class TestInvestmentPreferenceModel:
    """InvestmentPreference 모델 테스트"""

    def test_investment_preference_creation(self):
        """InvestmentPreference 생성 테스트"""
        preference = InvestmentPreference(
            user_id=1,
            risk_tolerance=7,
            target_return=Decimal("10.5"),
            investment_period="LONG"
        )
        assert preference.user_id == 1
        assert preference.risk_tolerance == 7
        assert preference.target_return == Decimal("10.5")
        assert preference.investment_period == "LONG"


class TestFinancialGoalModel:
    """FinancialGoal 모델 테스트"""

    def test_financial_goal_creation(self):
        """FinancialGoal 생성 테스트"""
        goal = FinancialGoal(
            user_id=1,
            goal_type="RETIREMENT",
            target_amount=Decimal("500000000"),
            target_date=date(2050, 1, 1),
            priority=1
        )
        assert goal.user_id == 1
        assert goal.goal_type == "RETIREMENT"
        assert goal.target_amount == Decimal("500000000")
        assert goal.current_progress == Decimal("0")


class TestInvestmentRecordModel:
    """InvestmentRecord 모델 테스트"""

    def test_investment_record_creation(self):
        """InvestmentRecord 생성 테스트"""
        record = InvestmentRecord(
            user_id=1,
            asset_type="STOCK",
            symbol="AAPL",
            quantity=Decimal("10.5"),
            buy_price=Decimal("150.00"),
            buy_date=date(2024, 1, 1)
        )
        assert record.user_id == 1
        assert record.asset_type == "STOCK"
        assert record.symbol == "AAPL"
        assert record.quantity == Decimal("10.5")
        assert record.realized is False




