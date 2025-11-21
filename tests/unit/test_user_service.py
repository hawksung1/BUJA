"""
UserService 단위 테스트
"""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import Database
from src.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from src.models import FinancialSituation, InvestmentPreference, User, UserProfile
from src.repositories import (
    FinancialSituationRepository,
    InvestmentPreferenceRepository,
    UserProfileRepository,
    UserRepository,
)
from src.services.user_service import UserService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    db = MagicMock(spec=Database)
    return db


@pytest.fixture
def mock_session():
    """Mock AsyncSession"""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def user_service(mock_db):
    """UserService 인스턴스"""
    return UserService(database=mock_db)


class TestUserServiceRegister:
    """UserService.register 테스트"""

    @pytest.mark.asyncio
    async def test_register_success(self, user_service, mock_db, mock_session):
        """회원가입 성공 테스트"""
        # Mock 설정
        new_user = User(id=1, email="test@example.com", password_hash="hashed")
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        mock_user_repo.create_user = AsyncMock(return_value=new_user)
        user_service.user_repo = mock_user_repo

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # 테스트 실행
        result = await user_service.register(
            email="test@example.com",
            password="password123"
        )

        assert result.email == "test@example.com"
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
        mock_user_repo.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, user_service, mock_db):
        """중복 이메일 회원가입 실패 테스트"""
        # Mock 설정
        existing_user = User(id=1, email="test@example.com", password_hash="hashed")
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_email = AsyncMock(return_value=existing_user)
        user_service.user_repo = mock_user_repo

        # 테스트 실행 및 검증
        with pytest.raises(UserAlreadyExistsError):
            await user_service.register(
                email="test@example.com",
                password="password123"
            )

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, user_service):
        """유효하지 않은 이메일 회원가입 실패 테스트"""
        with pytest.raises(ValidationError):
            await user_service.register(
                email="invalid-email",
                password="password123"
            )

    @pytest.mark.asyncio
    async def test_register_weak_password(self, user_service):
        """약한 비밀번호 회원가입 실패 테스트"""
        with pytest.raises(ValidationError):
            await user_service.register(
                email="test@example.com",
                password="123"  # 너무 짧음
            )


class TestUserServiceAuthenticate:
    """UserService.authenticate 테스트"""

    @pytest.mark.asyncio
    async def test_authenticate_success(self, user_service, mock_db):
        """로그인 성공 테스트"""
        # Mock 설정
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$hashedpassword",  # bcrypt 해시 형식
            is_active=True
        )
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_email = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        # verify_password를 mock
        with patch("src.services.user_service.verify_password", return_value=True):
            result = await user_service.authenticate(
                email="test@example.com",
                password="password123"
            )

            assert result == user
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, user_service, mock_db):
        """존재하지 않는 사용자 로그인 실패 테스트"""
        # Mock 설정
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        user_service.user_repo = mock_user_repo

        # 테스트 실행 및 검증
        with pytest.raises(InvalidCredentialsError):
            await user_service.authenticate(
                email="nonexistent@example.com",
                password="password123"
            )

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, user_service, mock_db):
        """잘못된 비밀번호 로그인 실패 테스트"""
        # Mock 설정
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$hashedpassword",
            is_active=True
        )
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_email = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        # verify_password를 mock (False 반환)
        with patch("src.services.user_service.verify_password", return_value=False):
            with pytest.raises(InvalidCredentialsError):
                await user_service.authenticate(
                    email="test@example.com",
                    password="wrongpassword"
                )


class TestUserServiceUpdateProfile:
    """UserService.update_profile 테스트"""

    @pytest.mark.asyncio
    async def test_update_profile_success(self, user_service, mock_db, mock_session):
        """프로필 업데이트 성공 테스트"""
        # Mock 설정
        user = User(id=1, email="test@example.com", password_hash="hashed")
        profile = UserProfile(id=1, user_id=1, name="Old Name", age=25)

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        mock_profile_repo = MagicMock(spec=UserProfileRepository)
        mock_profile_repo.get_by_user_id = AsyncMock(return_value=profile)
        mock_profile_repo.update = AsyncMock(return_value=profile)
        user_service.profile_repo = mock_profile_repo

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # 테스트 실행
        result = await user_service.update_profile(
            user_id=1,
            profile_data={"name": "New Name", "age": 30}
        )

        assert result.name == "New Name"
        assert result.age == 30
        mock_profile_repo.update.assert_called_once()


class TestUserServiceUpdateFinancialSituation:
    """UserService.update_financial_situation 테스트"""

    @pytest.mark.asyncio
    async def test_update_financial_situation_success(
        self, user_service, mock_db, mock_session
    ):
        """재무 상황 업데이트 성공 테스트"""
        # Mock 설정
        user = User(id=1, email="test@example.com", password_hash="hashed")
        financial = FinancialSituation(
            id=1,
            user_id=1,
            monthly_income=Decimal("5000000"),
            total_assets=Decimal("100000000")
        )

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        mock_financial_repo = MagicMock(spec=FinancialSituationRepository)
        mock_financial_repo.get_by_user_id = AsyncMock(return_value=financial)
        mock_financial_repo.update = AsyncMock(return_value=financial)
        user_service.financial_repo = mock_financial_repo

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # 테스트 실행
        result = await user_service.update_financial_situation(
            user_id=1,
            financial_data={
                "monthly_income": Decimal("6000000"),
                "total_assets": Decimal("120000000")
            }
        )

        assert result.monthly_income == Decimal("6000000")
        assert result.total_assets == Decimal("120000000")
        mock_financial_repo.update.assert_called_once()


class TestUserServiceUpdateInvestmentPreference:
    """UserService.update_investment_preference 테스트"""

    @pytest.mark.asyncio
    async def test_update_investment_preference_success(
        self, user_service, mock_db, mock_session
    ):
        """투자 성향 업데이트 성공 테스트"""
        # Mock 설정
        user = User(id=1, email="test@example.com", password_hash="hashed")
        preference = InvestmentPreference(
            id=1,
            user_id=1,
            risk_tolerance=5,
            target_return=Decimal("10.0")
        )

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        mock_preference_repo = MagicMock(spec=InvestmentPreferenceRepository)
        mock_preference_repo.get_by_user_id = AsyncMock(return_value=preference)
        mock_preference_repo.update = AsyncMock(return_value=preference)
        user_service.preference_repo = mock_preference_repo

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # 테스트 실행
        result = await user_service.update_investment_preference(
            user_id=1,
            preference_data={
                "risk_tolerance": 7,
                "target_return": Decimal("12.0")
            }
        )

        assert result.risk_tolerance == 7
        assert result.target_return == Decimal("12.0")
        mock_preference_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_investment_preference_invalid_risk_tolerance(
        self, user_service, mock_db
    ):
        """잘못된 위험 감수 성향 업데이트 실패 테스트"""
        # Mock 설정
        user = User(id=1, email="test@example.com", password_hash="hashed")
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        # 테스트 실행 및 검증
        with pytest.raises(ValidationError):
            await user_service.update_investment_preference(
                user_id=1,
                preference_data={"risk_tolerance": 15}  # 1-10 범위 초과
            )


class TestUserServiceGetUser:
    """UserService.get_user 테스트"""

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service):
        """사용자 조회 성공 테스트"""
        # Mock 설정
        user = User(id=1, email="test@example.com", password_hash="hashed")
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        # 테스트 실행
        result = await user_service.get_user(1)

        assert result == user
        assert result.id == 1
        assert result.email == "test@example.com"
        mock_user_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service):
        """존재하지 않는 사용자 조회 실패 테스트"""
        # Mock 설정
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=None)
        user_service.user_repo = mock_user_repo

        # 테스트 실행 및 검증
        with pytest.raises(UserNotFoundError):
            await user_service.get_user(999)


class TestUserServiceGetUserWithProfile:
    """UserService.get_user_with_profile 테스트"""

    @pytest.mark.asyncio
    async def test_get_user_with_profile_success(self, user_service):
        """프로필과 함께 사용자 조회 성공 테스트"""
        # Mock 설정
        profile = UserProfile(id=1, user_id=1, name="Test User", age=30)
        user = User(id=1, email="test@example.com", password_hash="hashed")
        user.profile = profile

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_with_profile = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        # 테스트 실행
        result = await user_service.get_user_with_profile(1)

        assert result == user
        assert result.profile == profile
        assert result.profile.name == "Test User"
        mock_user_repo.get_with_profile.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_with_profile_not_found(self, user_service):
        """존재하지 않는 사용자 조회 실패 테스트"""
        # Mock 설정
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_with_profile = AsyncMock(return_value=None)
        user_service.user_repo = mock_user_repo

        # 테스트 실행 및 검증
        with pytest.raises(UserNotFoundError):
            await user_service.get_user_with_profile(999)


class TestUserServiceChangePassword:
    """UserService.change_password 테스트"""

    @pytest.mark.asyncio
    async def test_change_password_success(self, user_service, mock_db, mock_session):
        """비밀번호 변경 성공 테스트"""
        # Mock 설정
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$oldhash",
            is_active=True
        )
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        mock_user_repo.update = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()

        # verify_password와 hash_password를 mock
        with patch("src.services.user_service.verify_password", return_value=True), \
             patch("src.services.user_service.hash_password", return_value="$2b$12$newhash"):
            result = await user_service.change_password(
                user_id=1,
                old_password="oldpassword",
                new_password="newpassword123"
            )

            assert result is True
            mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, user_service):
        """잘못된 기존 비밀번호로 변경 실패 테스트"""
        # Mock 설정
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$oldhash",
            is_active=True
        )
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        # verify_password를 mock (False 반환)
        with patch("src.services.user_service.verify_password", return_value=False):
            with pytest.raises(InvalidCredentialsError):
                await user_service.change_password(
                    user_id=1,
                    old_password="wrongpassword",
                    new_password="newpassword123"
                )

    @pytest.mark.asyncio
    async def test_change_password_weak_new_password(self, user_service):
        """약한 새 비밀번호로 변경 실패 테스트"""
        # Mock 설정
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$oldhash",
            is_active=True
        )
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        # verify_password를 mock (True 반환)
        with patch("src.services.user_service.verify_password", return_value=True):
            with pytest.raises(ValidationError):
                await user_service.change_password(
                    user_id=1,
                    old_password="oldpassword",
                    new_password="123"  # 너무 짧음
                )


class TestUserServiceDeactivateUser:
    """UserService.deactivate_user 테스트"""

    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, user_service, mock_db, mock_session):
        """사용자 계정 비활성화 성공 테스트"""
        # Mock 설정
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed",
            is_active=True
        )
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=user)
        mock_user_repo.update = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()

        # 테스트 실행
        result = await user_service.deactivate_user(1)

        assert result is True
        assert user.is_active is False
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_user_not_found(self, user_service):
        """존재하지 않는 사용자 비활성화 실패 테스트"""
        # Mock 설정
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_id = AsyncMock(return_value=None)
        user_service.user_repo = mock_user_repo

        # 테스트 실행 및 검증
        with pytest.raises(UserNotFoundError):
            await user_service.deactivate_user(999)


class TestUserServiceAuthenticateInactive:
    """UserService.authenticate - 비활성 계정 테스트"""

    @pytest.mark.asyncio
    async def test_authenticate_inactive_account(self, user_service):
        """비활성 계정 로그인 실패 테스트"""
        # Mock 설정
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$hashedpassword",
            is_active=False  # 비활성 계정
        )
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_by_email = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        # verify_password를 mock (True 반환)
        with patch("src.services.user_service.verify_password", return_value=True):
            with pytest.raises(InvalidCredentialsError):
                await user_service.authenticate(
                    email="test@example.com",
                    password="password123"
                )
