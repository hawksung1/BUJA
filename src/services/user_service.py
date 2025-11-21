"""
사용자 관리 및 인증 서비스
"""
from typing import Any, Dict, Optional

from config.database import Database, db
from config.logging import get_logger
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
from src.utils.security import hash_password, verify_password
from src.utils.validators import validate_email, validate_password

logger = get_logger(__name__)


class UserService:
    """사용자 관리 및 인증 서비스"""

    def __init__(self, database: Optional[Database] = None):
        """
        UserService 초기화
        
        Args:
            database: Database 인스턴스 (기본값: 전역 db 인스턴스)
        """
        self.db = database or db
        self.user_repo = UserRepository(self.db)
        self.profile_repo = UserProfileRepository(self.db)
        self.financial_repo = FinancialSituationRepository(self.db)
        self.preference_repo = InvestmentPreferenceRepository(self.db)

    async def register(
        self,
        email: str,
        password: str,
        profile_data: Optional[Dict[str, Any]] = None,
        skip_validation: bool = False
    ) -> User:
        """
        사용자 회원가입
        
        Args:
            email: 이메일 주소
            password: 평문 비밀번호
            profile_data: 프로필 데이터 (선택사항)
                - name: 이름
                - age: 나이
                - occupation: 직업
            skip_validation: 검증 건너뛰기 (admin 계정 등 특수한 경우)
        
        Returns:
            생성된 User 객체
        
        Raises:
            UserAlreadyExistsError: 이미 존재하는 이메일인 경우
            ValidationError: 이메일 또는 비밀번호 형식이 잘못된 경우
        """
        # 이메일 및 비밀번호 검증 (skip_validation이 False인 경우만)
        if not skip_validation:
            if not validate_email(email):
                raise ValidationError("Invalid email format.")

            if not validate_password(password):
                raise ValidationError("Password must be at least 8 characters long.")
        else:
            # 최소한의 검증
            if not email or not password:
                raise ValidationError("Email and password are required.")

        # Check email duplication
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(f"Email already exists: {email}")

        # 비밀번호 해싱
        password_hash = hash_password(password)

        # 사용자 생성
        async with self.db.session() as session:
            user = await self.user_repo.create_user(
                email=email,
                password_hash=password_hash,
                session=session
            )

            # 프로필 데이터가 있으면 프로필 생성
            if profile_data:
                profile = UserProfile(
                    user_id=user.id,
                    name=profile_data.get("name"),
                    age=profile_data.get("age"),
                    occupation=profile_data.get("occupation"),
                )
                await self.profile_repo.create(profile, session=session)

            await session.commit()
            await session.refresh(user)

            logger.info(f"User registered: {email}", extra={"user_id": user.id})
            return user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        사용자 인증 (로그인)
        
        Args:
            email: 이메일 주소
            password: 평문 비밀번호
        
        Returns:
            인증 성공 시 User 객체, 실패 시 None
        
        Raises:
            InvalidCredentialsError: 잘못된 인증 정보인 경우
        """
        # Get user
        user = await self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            raise InvalidCredentialsError("Invalid email or password.")

        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Login attempt with wrong password: {email}")
            raise InvalidCredentialsError("Invalid email or password.")

        # Check account activation
        if not user.is_active:
            logger.warning(f"Login attempt with inactive account: {email}")
            raise InvalidCredentialsError("Account is deactivated.")

        logger.info(f"User authenticated: {email}", extra={"user_id": user.id})
        return user

    async def get_user(self, user_id: int) -> User:
        """
        사용자 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            User 객체
        
        Raises:
            UserNotFoundError: 사용자를 찾을 수 없는 경우
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User not found: {user_id}")
        return user

    async def get_user_with_profile(self, user_id: int) -> User:
        """
        프로필과 함께 사용자 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            User 객체 (프로필 포함)
        
        Raises:
            UserNotFoundError: 사용자를 찾을 수 없는 경우
        """
        user = await self.user_repo.get_with_profile(user_id)
        if not user:
            raise UserNotFoundError(f"User not found: {user_id}")
        return user

    async def update_profile(
        self,
        user_id: int,
        profile_data: Dict[str, Any]
    ) -> UserProfile:
        """
        사용자 프로필 업데이트
        
        Args:
            user_id: 사용자 ID
            profile_data: 프로필 데이터
                - name: 이름
                - age: 나이
                - occupation: 직업
        
        Returns:
            업데이트된 UserProfile 객체
        
        Raises:
            UserNotFoundError: 사용자를 찾을 수 없는 경우
        """
        # 사용자 존재 확인
        user = await self.get_user(user_id)

        async with self.db.session() as session:
            # 기존 프로필 조회 또는 생성
            profile = await self.profile_repo.get_by_user_id(user_id, session=session)

            if profile:
                # 프로필 업데이트
                if "name" in profile_data:
                    profile.name = profile_data["name"]
                if "age" in profile_data:
                    profile.age = profile_data["age"]
                if "occupation" in profile_data:
                    profile.occupation = profile_data["occupation"]

                profile = await self.profile_repo.update(profile, session=session)
            else:
                # 새 프로필 생성
                profile = UserProfile(
                    user_id=user_id,
                    name=profile_data.get("name"),
                    age=profile_data.get("age"),
                    occupation=profile_data.get("occupation"),
                )
                profile = await self.profile_repo.create(profile, session=session)

            await session.commit()
            await session.refresh(profile)

            logger.info(f"Profile updated: user_id={user_id}")
            return profile

    async def update_financial_situation(
        self,
        user_id: int,
        financial_data: Dict[str, Any]
    ) -> FinancialSituation:
        """
        재무 상황 업데이트
        
        Args:
            user_id: 사용자 ID
            financial_data: 재무 데이터
                - monthly_income: 월 소득
                - monthly_expense: 월 지출
                - total_assets: 총 자산
                - total_debt: 총 부채
                - emergency_fund: 비상자금
                - family_members: 가족 구성원 수
                - insurance_coverage: 보험 가입 현황
        
        Returns:
            업데이트된 FinancialSituation 객체
        
        Raises:
            UserNotFoundError: 사용자를 찾을 수 없는 경우
        """
        # 사용자 존재 확인
        await self.get_user(user_id)

        async with self.db.session() as session:
            # 기존 재무 상황 조회 또는 생성
            financial = await self.financial_repo.get_by_user_id(user_id, session=session)

            if financial:
                # 재무 상황 업데이트
                if "monthly_income" in financial_data:
                    financial.monthly_income = financial_data["monthly_income"]
                if "monthly_expense" in financial_data:
                    financial.monthly_expense = financial_data["monthly_expense"]
                if "total_assets" in financial_data:
                    financial.total_assets = financial_data["total_assets"]
                if "total_debt" in financial_data:
                    financial.total_debt = financial_data["total_debt"]
                if "emergency_fund" in financial_data:
                    financial.emergency_fund = financial_data["emergency_fund"]
                if "family_members" in financial_data:
                    financial.family_members = financial_data["family_members"]
                if "insurance_coverage" in financial_data:
                    financial.insurance_coverage = financial_data["insurance_coverage"]

                financial = await self.financial_repo.update(financial, session=session)
            else:
                # 새 재무 상황 생성
                financial = FinancialSituation(
                    user_id=user_id,
                    monthly_income=financial_data.get("monthly_income"),
                    monthly_expense=financial_data.get("monthly_expense"),
                    total_assets=financial_data.get("total_assets"),
                    total_debt=financial_data.get("total_debt"),
                    emergency_fund=financial_data.get("emergency_fund"),
                    family_members=financial_data.get("family_members"),
                    insurance_coverage=financial_data.get("insurance_coverage"),
                )
                financial = await self.financial_repo.create(financial, session=session)

            await session.commit()
            await session.refresh(financial)

            logger.info(f"Financial situation updated: user_id={user_id}")
            return financial

    async def update_investment_preference(
        self,
        user_id: int,
        preference_data: Dict[str, Any]
    ) -> InvestmentPreference:
        """
        투자 성향 업데이트
        
        Args:
            user_id: 사용자 ID
            preference_data: 투자 성향 데이터
                - risk_tolerance: 위험 감수 성향 (1-10)
                - target_return: 목표 수익률
                - investment_period: 투자 기간 (SHORT, MEDIUM, LONG)
                - preferred_asset_types: 선호 자산 유형 리스트
                - max_loss_tolerance: 최대 손실 허용 범위
                - investment_experience: 투자 경험 수준 (BEGINNER, INTERMEDIATE, ADVANCED)
        
        Returns:
            업데이트된 InvestmentPreference 객체
        
        Raises:
            UserNotFoundError: 사용자를 찾을 수 없는 경우
            ValidationError: 잘못된 데이터인 경우
        """
        # 사용자 존재 확인
        await self.get_user(user_id)

        # Validate risk tolerance
        if "risk_tolerance" in preference_data:
            risk_tolerance = preference_data["risk_tolerance"]
            if not isinstance(risk_tolerance, int) or risk_tolerance < 1 or risk_tolerance > 10:
                raise ValidationError("Risk tolerance must be an integer between 1 and 10.")

        async with self.db.session() as session:
            # 기존 투자 성향 조회 또는 생성
            preference = await self.preference_repo.get_by_user_id(user_id, session=session)

            if preference:
                # 투자 성향 업데이트
                if "risk_tolerance" in preference_data:
                    preference.risk_tolerance = preference_data["risk_tolerance"]
                if "target_return" in preference_data:
                    preference.target_return = preference_data["target_return"]
                if "investment_period" in preference_data:
                    preference.investment_period = preference_data["investment_period"]
                if "preferred_asset_types" in preference_data:
                    preference.preferred_asset_types = preference_data["preferred_asset_types"]
                if "max_loss_tolerance" in preference_data:
                    preference.max_loss_tolerance = preference_data["max_loss_tolerance"]
                if "investment_experience" in preference_data:
                    preference.investment_experience = preference_data["investment_experience"]
                if "preferred_regions" in preference_data:
                    preference.preferred_regions = preference_data["preferred_regions"]
                if "currency_hedge_preference" in preference_data:
                    preference.currency_hedge_preference = preference_data["currency_hedge_preference"]
                if "home_country" in preference_data:
                    preference.home_country = preference_data["home_country"]

                preference = await self.preference_repo.update(preference, session=session)
            else:
                # Create new investment preference
                if "risk_tolerance" not in preference_data:
                    raise ValidationError("risk_tolerance is required.")

                preference = InvestmentPreference(
                    user_id=user_id,
                    risk_tolerance=preference_data["risk_tolerance"],
                    target_return=preference_data.get("target_return"),
                    investment_period=preference_data.get("investment_period"),
                    preferred_asset_types=preference_data.get("preferred_asset_types"),
                    max_loss_tolerance=preference_data.get("max_loss_tolerance"),
                    investment_experience=preference_data.get("investment_experience"),
                    preferred_regions=preference_data.get("preferred_regions"),
                    currency_hedge_preference=preference_data.get("currency_hedge_preference"),
                    home_country=preference_data.get("home_country"),
                )
                preference = await self.preference_repo.create(preference, session=session)

            await session.commit()
            await session.refresh(preference)

            logger.info(f"Investment preference updated: user_id={user_id}")
            return preference

    async def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        비밀번호 변경
        
        Args:
            user_id: 사용자 ID
            old_password: 기존 비밀번호
            new_password: 새 비밀번호
        
        Returns:
            변경 성공 여부
        
        Raises:
            UserNotFoundError: 사용자를 찾을 수 없는 경우
            InvalidCredentialsError: 기존 비밀번호가 올바르지 않은 경우
            ValidationError: 새 비밀번호 형식이 잘못된 경우
        """
        # 사용자 조회
        user = await self.get_user(user_id)

        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect.")

        # Validate new password
        if not validate_password(new_password):
            raise ValidationError("Password must be at least 8 characters long.")

        # 비밀번호 변경
        new_password_hash = hash_password(new_password)

        async with self.db.session() as session:
            user.password_hash = new_password_hash
            await self.user_repo.update(user, session=session)
            await session.commit()

            logger.info(f"Password changed: user_id={user_id}")
            return True

    async def deactivate_user(self, user_id: int) -> bool:
        """
        사용자 계정 비활성화
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            비활성화 성공 여부
        
        Raises:
            UserNotFoundError: 사용자를 찾을 수 없는 경우
        """
        user = await self.get_user(user_id)

        async with self.db.session() as session:
            user.is_active = False
            await self.user_repo.update(user, session=session)
            await session.commit()

            logger.info(f"User deactivated: user_id={user_id}")
            return True

