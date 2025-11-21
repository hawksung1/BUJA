"""
글로벌 포트폴리오 구성 테스트
"""
from decimal import Decimal

import pytest

from src.analyzers.asset_allocator import AssetAllocator
from src.services.currency_hedge_service import CurrencyHedgeService


class TestGlobalPortfolioAllocation:
    """글로벌 포트폴리오 배분 테스트"""

    def test_calculate_global_allocation_basic(self):
        """기본 글로벌 포트폴리오 배분 테스트"""
        allocator = AssetAllocator()

        result = allocator.calculate_initial_allocation(
            risk_tolerance=5,
            initial_amount=Decimal("100000000"),  # 1억원
            preferred_regions=["KOREA", "USA", "EUROPE"],
            home_country="KOREA",
            currency_hedge_preference="PARTIAL"
        )

        assert "global_allocation" in result
        assert result["global_allocation"]["home_country"] == "KOREA"
        assert "regions" in result["global_allocation"]
        assert "currencies" in result["global_allocation"]
        assert "hedge_strategy" in result["global_allocation"]

        # 지역별 배분 확인
        regions = result["global_allocation"]["regions"]
        assert "KOREA" in regions
        assert "USA" in regions
        assert "EUROPE" in regions

        # 본국 비중이 더 높아야 함
        assert regions["KOREA"]["weight"] > regions["USA"]["weight"]

    def test_currency_hedge_ratio_calculation(self):
        """환율 헷지 비율 계산 테스트"""
        hedge_service = CurrencyHedgeService()

        # NONE 헷지
        ratio_none = hedge_service.calculate_hedge_ratio("NONE", 5)
        assert ratio_none == 0.0

        # PARTIAL 헷지
        ratio_partial = hedge_service.calculate_hedge_ratio("PARTIAL", 5, "MEDIUM")
        assert 0.3 <= ratio_partial <= 0.8

        # FULL 헷지
        ratio_full = hedge_service.calculate_hedge_ratio("FULL", 5)
        assert 0.7 <= ratio_full <= 1.0

    def test_currency_allocation_with_hedge(self):
        """헷지 포함 통화 배분 테스트"""
        hedge_service = CurrencyHedgeService()

        allocation = hedge_service.calculate_currency_allocation(
            preferred_regions=["KOREA", "USA", "EUROPE"],
            home_country="KOREA",
            total_amount=Decimal("100000000"),
            hedge_ratio=0.5
        )

        assert "KRW" in allocation
        assert "USD" in allocation
        assert "EUR" in allocation

        # 본국 통화 비중이 높아야 함
        assert allocation["KRW"]["weight"] > allocation["USD"]["weight"]

        # 헷지 적용 확인
        for currency, details in allocation.items():
            if currency != "KRW":
                assert "hedged_amount" in details
                assert "unhedged_amount" in details
                assert details["hedged"] is True

    def test_region_allocation_distribution(self):
        """지역별 배분 균형 테스트"""
        allocator = AssetAllocator()

        # 여러 지역 선택 시
        result1 = allocator._calculate_region_allocation(
            preferred_regions=["KOREA", "USA", "EUROPE", "ASIA"],
            home_country="KOREA",
            total_amount=Decimal("100000000")
        )

        total_weight = sum(r["weight"] for r in result1.values())
        assert abs(total_weight - 1.0) < 0.01  # 100%에 가까워야 함

        # 본국 비중 확인
        assert result1["KOREA"]["weight"] > 0.3  # 본국은 최소 30% 이상

    def test_hedge_strategy_generation(self):
        """헷지 전략 생성 테스트"""
        hedge_service = CurrencyHedgeService()

        currency_allocation = {
            "KRW": {
                "weight": 0.4,
                "amount": 40000000,
                "hedged": False
            },
            "USD": {
                "weight": 0.3,
                "amount": 30000000,
                "hedged_amount": 15000000,
                "unhedged_amount": 15000000,
                "hedged": True,
                "hedge_ratio": 0.5
            }
        }

        strategy = hedge_service.generate_hedge_strategy(
            currency_allocation=currency_allocation,
            hedge_preference="PARTIAL"
        )

        assert strategy["hedge_preference"] == "PARTIAL"
        assert strategy["total_hedged_amount"] > 0
        assert len(strategy["recommendations"]) > 0

    def test_global_allocation_with_different_risk_levels(self):
        """다양한 위험 수준에서의 글로벌 포트폴리오 테스트"""
        allocator = AssetAllocator()

        for risk in [1, 5, 10]:
            result = allocator.calculate_initial_allocation(
                risk_tolerance=risk,
                initial_amount=Decimal("100000000"),
                preferred_regions=["KOREA", "USA"],
                home_country="KOREA",
                currency_hedge_preference="PARTIAL"
            )

            assert "global_allocation" in result
            # 위험 수준에 따라 헷지 비율이 달라져야 함
            hedge_ratio = result["global_allocation"]["hedge_strategy"]["hedge_ratio"]
            assert 0.0 <= hedge_ratio <= 1.0


class TestCurrencyHedgeService:
    """환율 헷지 서비스 테스트"""

    def test_currency_mapping(self):
        """통화 매핑 테스트"""
        hedge_service = CurrencyHedgeService()

        assert hedge_service.CURRENCIES["KOREA"] == "KRW"
        assert hedge_service.CURRENCIES["USA"] == "USD"
        assert hedge_service.CURRENCIES["EUROPE"] == "EUR"

    def test_region_currencies(self):
        """지역별 통화 리스트 테스트"""
        hedge_service = CurrencyHedgeService()

        asia_currencies = hedge_service.REGION_CURRENCIES["ASIA"]
        assert "JPY" in asia_currencies
        assert "CNY" in asia_currencies
        assert "KRW" in asia_currencies

    def test_hedge_ratio_with_investment_period(self):
        """투자 기간에 따른 헷지 비율 조정 테스트"""
        hedge_service = CurrencyHedgeService()

        # SHORT 기간은 헷지 비율이 높아야 함
        ratio_short = hedge_service.calculate_hedge_ratio("PARTIAL", 5, "SHORT")
        ratio_long = hedge_service.calculate_hedge_ratio("PARTIAL", 5, "LONG")

        assert ratio_short > ratio_long


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

