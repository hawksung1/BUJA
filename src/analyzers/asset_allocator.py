"""
자산 배분 분석기
"""
from decimal import Decimal
from typing import Any, Dict, List, Optional

from config.logging import get_logger

logger = get_logger(__name__)


class AssetAllocator:
    """자산 배분 분석기"""

    # 위험 수준별 기본 자산 배분 템플릿
    CONSERVATIVE_ALLOCATION = {
        "stock": 30,
        "bond": 50,
        "cash": 15,
        "alternative": 5
    }

    MODERATE_ALLOCATION = {
        "stock": 60,
        "bond": 30,
        "cash": 5,
        "alternative": 5
    }

    AGGRESSIVE_ALLOCATION = {
        "stock": 70,
        "bond": 15,
        "cash": 5,
        "alternative": 10
    }

    def calculate_allocation(
        self,
        risk_tolerance: int,
        total_amount: Optional[Decimal] = None,
        preferred_types: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        투자 성향 기반 자산 배분 계산
        
        Args:
            risk_tolerance: 위험 감수 성향 (1-10)
            total_amount: 총 투자 금액 (선택사항)
            preferred_types: 선호 자산 유형 리스트 (선택사항)
        
        Returns:
            자산 배분 딕셔너리
        """
        # 위험 수준에 따른 기본 배분 선택
        if risk_tolerance <= 3:
            base_allocation = self.CONSERVATIVE_ALLOCATION.copy()
            risk_level = "보수적"
        elif risk_tolerance <= 6:
            base_allocation = self.MODERATE_ALLOCATION.copy()
            risk_level = "중립"
        else:
            base_allocation = self.AGGRESSIVE_ALLOCATION.copy()
            risk_level = "공격적"

        # 선호 자산 유형이 있으면 조정
        if preferred_types:
            allocation = self._adjust_for_preferences(base_allocation, preferred_types)
        else:
            allocation = base_allocation.copy()

        # 금액이 있으면 금액 계산
        if total_amount:
            allocation_amounts = {
                asset_type: float(total_amount) * (percentage / 100)
                for asset_type, percentage in allocation.items()
            }
            result = {
                "allocation_percentages": allocation,
                "allocation_amounts": allocation_amounts,
                "total_amount": float(total_amount),
                "risk_level": risk_level,
                "risk_tolerance": risk_tolerance
            }
        else:
            result = {
                "allocation_percentages": allocation,
                "risk_level": risk_level,
                "risk_tolerance": risk_tolerance
            }

        return result

    def _adjust_for_preferences(
        self,
        base_allocation: Dict[str, float],
        preferred_types: list[str]
    ) -> Dict[str, float]:
        """
        선호 자산 유형에 따라 배분 조정
        
        Args:
            base_allocation: 기본 배분
            preferred_types: 선호 자산 유형 리스트
        
        Returns:
            조정된 배분
        """
        allocation = base_allocation.copy()

        # 선호 유형에 따라 가중치 조정
        if "STOCK" in preferred_types:
            allocation["stock"] = min(80, allocation["stock"] + 10)
        if "BOND" in preferred_types:
            allocation["bond"] = min(60, allocation["bond"] + 10)
        if "CRYPTO" in preferred_types:
            allocation["alternative"] = min(20, allocation["alternative"] + 5)

        # 총합이 100이 되도록 정규화
        total = sum(allocation.values())
        if total != 100:
            allocation = {
                k: (v / total) * 100
                for k, v in allocation.items()
            }

        return allocation

    def calculate_initial_allocation(
        self,
        risk_tolerance: int,
        initial_amount: Decimal,
        preferred_types: Optional[list[str]] = None,
        preferred_regions: Optional[list[str]] = None,
        home_country: Optional[str] = None,
        currency_hedge_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        최초 자산 구성 추천 (글로벌 포트폴리오 포함)
        
        Args:
            risk_tolerance: 위험 감수 성향 (1-10)
            initial_amount: 초기 투자 금액
            preferred_types: 선호 자산 유형 리스트 (선택사항)
            preferred_regions: 선호 투자 지역 리스트 (선택사항)
            home_country: 거주 국가 (선택사항)
            currency_hedge_preference: 환율 헷지 선호도 (NONE, PARTIAL, FULL)
        
        Returns:
            초기 자산 구성 추천 딕셔너리 (글로벌 포트폴리오 정보 포함)
        """
        allocation = self.calculate_allocation(
            risk_tolerance=risk_tolerance,
            total_amount=initial_amount,
            preferred_types=preferred_types
        )

        # 글로벌 포트폴리오 구성 추가
        if preferred_regions or home_country:
            global_allocation = self._calculate_global_allocation(
                preferred_regions=preferred_regions or ["KOREA", "USA"],
                home_country=home_country or "KOREA",
                total_amount=initial_amount,
                currency_hedge_preference=currency_hedge_preference or "PARTIAL",
                risk_tolerance=risk_tolerance
            )
            allocation["global_allocation"] = global_allocation

        # 초기 구성에 대한 추가 정보
        allocation["recommendation_type"] = "INITIAL"
        allocation["reasoning"] = self._generate_initial_reasoning(
            risk_tolerance,
            initial_amount,
            allocation["risk_level"],
            preferred_regions=preferred_regions
        )

        return allocation

    def _calculate_global_allocation(
        self,
        preferred_regions: List[str],
        home_country: str,
        total_amount: Decimal,
        currency_hedge_preference: str,
        risk_tolerance: int
    ) -> Dict[str, Any]:
        """
        글로벌 포트폴리오 배분 계산
        
        Args:
            preferred_regions: 선호 투자 지역 리스트
            home_country: 거주 국가
            total_amount: 총 투자 금액
            currency_hedge_preference: 환율 헷지 선호도
            risk_tolerance: 위험 감수 성향
        
        Returns:
            글로벌 배분 딕셔너리
        """
        from src.services.currency_hedge_service import CurrencyHedgeService

        hedge_service = CurrencyHedgeService()

        # 헷지 비율 계산
        hedge_ratio = hedge_service.calculate_hedge_ratio(
            hedge_preference=currency_hedge_preference,
            risk_tolerance=risk_tolerance
        )

        # 통화별 배분 계산
        currency_allocation = hedge_service.calculate_currency_allocation(
            preferred_regions=preferred_regions,
            home_country=home_country,
            total_amount=total_amount,
            hedge_ratio=hedge_ratio
        )

        # 지역별 배분 계산
        region_allocation = self._calculate_region_allocation(
            preferred_regions=preferred_regions,
            home_country=home_country,
            total_amount=total_amount
        )

        # 헷지 전략 생성
        hedge_strategy = hedge_service.generate_hedge_strategy(
            currency_allocation=currency_allocation,
            hedge_preference=currency_hedge_preference
        )

        return {
            "regions": region_allocation,
            "currencies": currency_allocation,
            "hedge_strategy": hedge_strategy,
            "home_country": home_country,
            "preferred_regions": preferred_regions
        }

    def _calculate_region_allocation(
        self,
        preferred_regions: List[str],
        home_country: str,
        total_amount: Decimal
    ) -> Dict[str, Dict[str, Any]]:
        """
        지역별 자산 배분 계산
        
        Args:
            preferred_regions: 선호 투자 지역 리스트
            home_country: 거주 국가
            total_amount: 총 투자 금액
        
        Returns:
            지역별 배분 딕셔너리
        """
        # 기본 가중치: 본국 40%, 나머지 균등 분배
        num_regions = len(preferred_regions)
        if num_regions == 0:
            return {}

        home_weight = 0.4
        other_weight_per_region = (1.0 - home_weight) / max(1, num_regions - (1 if home_country in preferred_regions else 0))

        region_allocation = {}
        for region in preferred_regions:
            if region == home_country:
                weight = home_weight
            else:
                weight = other_weight_per_region

            region_allocation[region] = {
                "weight": weight,
                "amount": float(total_amount) * weight,
                "percentage": weight * 100
            }

        return region_allocation

    def _generate_initial_reasoning(
        self,
        risk_tolerance: int,
        amount: Decimal,
        risk_level: str,
        preferred_regions: Optional[List[str]] = None
    ) -> str:
        """
        초기 구성 추천 근거 생성
        
        Args:
            risk_tolerance: 위험 감수 성향
            amount: 투자 금액
            risk_level: 위험 수준
            preferred_regions: 선호 투자 지역 리스트
        
        Returns:
            추천 근거 문자열
        """
        base_reasoning = (
            f"귀하의 위험 감수 성향({risk_tolerance}/10, {risk_level})을 고려하여 "
            f"초기 투자 금액 {amount:,.0f}원에 대한 자산 배분을 추천합니다. "
            f"이 배분은 귀하의 투자 목표와 위험 감수 능력에 맞춰 설계되었습니다."
        )

        if preferred_regions and len(preferred_regions) > 1:
            regions_str = ", ".join(preferred_regions)
            base_reasoning += (
                f" 또한 {regions_str} 지역에 자산을 분산 배치하여 "
                f"지역별 경제 사이클 차이를 활용한 리스크 분산과 성장 기회를 추구합니다."
            )

        return base_reasoning

