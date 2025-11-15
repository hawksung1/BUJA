"""
글로벌 포트폴리오 시나리오 테스트
전문 자산 포트폴리오 관리사 수준의 검증
"""
import pytest
from decimal import Decimal
from src.analyzers.asset_allocator import AssetAllocator
from src.services.currency_hedge_service import CurrencyHedgeService
from src.services.recommendation_service import RecommendationService


class TestGlobalPortfolioScenarios:
    """글로벌 포트폴리오 시나리오 테스트"""
    
    def test_scenario_1_korean_investor_global_diversification(self):
        """
        시나리오 1: 한국 거주 투자자, 글로벌 분산 투자
        - 거주 국가: 한국
        - 선호 지역: 한국, 미국, 유럽, 아시아
        - 환율 헷지: 부분 헷지
        - 위험 감수 성향: 중립 (5)
        """
        allocator = AssetAllocator()
        
        result = allocator.calculate_initial_allocation(
            risk_tolerance=5,
            initial_amount=Decimal("500000000"),  # 5억원
            preferred_regions=["KOREA", "USA", "EUROPE", "ASIA"],
            home_country="KOREA",
            currency_hedge_preference="PARTIAL"
        )
        
        # 검증
        assert "global_allocation" in result
        global_alloc = result["global_allocation"]
        
        # 지역 분산 확인
        regions = global_alloc["regions"]
        assert len(regions) == 4
        assert "KOREA" in regions
        assert regions["KOREA"]["weight"] > 0.3  # 본국 비중 30% 이상
        
        # 통화 분산 확인
        currencies = global_alloc["currencies"]
        assert "KRW" in currencies
        assert "USD" in currencies
        assert "EUR" in currencies or "JPY" in currencies or "CNY" in currencies
        
        # 헷지 전략 확인
        hedge_strategy = global_alloc["hedge_strategy"]
        assert hedge_strategy["hedge_preference"] == "PARTIAL"
        assert 0.3 <= hedge_strategy["hedge_ratio"] <= 0.8
    
    def test_scenario_2_aggressive_investor_no_hedge(self):
        """
        시나리오 2: 공격적 투자자, 헷지 없음
        - 거주 국가: 미국
        - 선호 지역: 미국, 신흥국
        - 환율 헷지: 없음
        - 위험 감수 성향: 공격적 (9)
        """
        allocator = AssetAllocator()
        
        result = allocator.calculate_initial_allocation(
            risk_tolerance=9,
            initial_amount=Decimal("1000000000"),  # 10억원
            preferred_regions=["USA", "EMERGING"],
            home_country="USA",
            currency_hedge_preference="NONE"
        )
        
        # 검증
        global_alloc = result["global_allocation"]
        hedge_strategy = global_alloc["hedge_strategy"]
        
        # 헷지 없음 확인
        assert hedge_strategy["hedge_preference"] == "NONE"
        assert hedge_strategy["hedge_ratio"] == 0.0
        
        # 공격적 배분 확인 (주식 비중 높음)
        assert result["allocation_percentages"]["stock"] > 60
    
    def test_scenario_3_conservative_investor_full_hedge(self):
        """
        시나리오 3: 보수적 투자자, 전체 헷지
        - 거주 국가: 일본
        - 선호 지역: 일본, 유럽
        - 환율 헷지: 전체 헷지
        - 위험 감수 성향: 보수적 (2)
        """
        allocator = AssetAllocator()
        
        result = allocator.calculate_initial_allocation(
            risk_tolerance=2,
            initial_amount=Decimal("200000000"),  # 2억원
            preferred_regions=["JAPAN", "EUROPE"],
            home_country="JAPAN",
            currency_hedge_preference="FULL"
        )
        
        # 검증
        global_alloc = result["global_allocation"]
        hedge_strategy = global_alloc["hedge_strategy"]
        
        # 전체 헷지 확인
        assert hedge_strategy["hedge_preference"] == "FULL"
        assert hedge_strategy["hedge_ratio"] >= 0.7
        
        # 보수적 배분 확인 (채권 비중 높음)
        assert result["allocation_percentages"]["bond"] > 40
    
    def test_scenario_4_multi_region_currency_diversification(self):
        """
        시나리오 4: 다중 지역 통화 분산
        - 거주 국가: 싱가포르
        - 선호 지역: 아시아, 유럽, 미국
        - 환율 헷지: 부분 헷지
        - 위험 감수 성향: 중립 (6)
        """
        allocator = AssetAllocator()
        hedge_service = CurrencyHedgeService()
        
        result = allocator.calculate_initial_allocation(
            risk_tolerance=6,
            initial_amount=Decimal("300000000"),  # 3억원
            preferred_regions=["ASIA", "EUROPE", "USA"],
            home_country="SINGAPORE",
            currency_hedge_preference="PARTIAL"
        )
        
        # 검증
        global_alloc = result["global_allocation"]
        currencies = global_alloc["currencies"]
        
        # 다중 통화 확인
        assert len(currencies) >= 3
        assert "SGD" in currencies  # 본국 통화
        assert "USD" in currencies or "EUR" in currencies or "JPY" in currencies
        
        # 통화별 헷지 적용 확인
        for currency, details in currencies.items():
            if currency != "SGD":
                assert "hedged_amount" in details
                assert "unhedged_amount" in details
    
    def test_scenario_5_emerging_market_focus(self):
        """
        시나리오 5: 신흥 시장 집중 투자
        - 거주 국가: 한국
        - 선호 지역: 신흥국, 아시아
        - 환율 헷지: 부분 헷지
        - 위험 감수 성향: 공격적 (8)
        """
        allocator = AssetAllocator()
        
        result = allocator.calculate_initial_allocation(
            risk_tolerance=8,
            initial_amount=Decimal("1000000000"),  # 10억원
            preferred_regions=["EMERGING", "ASIA"],
            home_country="KOREA",
            currency_hedge_preference="PARTIAL"
        )
        
        # 검증
        global_alloc = result["global_allocation"]
        currencies = global_alloc["currencies"]
        
        # 신흥국 통화 포함 확인
        emerging_currencies = ["BRL", "MXN", "INR", "ZAR", "TRY"]
        has_emerging = any(curr in currencies for curr in emerging_currencies)
        assert has_emerging or "CNY" in currencies or "JPY" in currencies
    
    def test_currency_hedge_ratio_calculation_scenarios(self):
        """환율 헷지 비율 계산 시나리오 테스트"""
        hedge_service = CurrencyHedgeService()
        
        # 시나리오 1: 보수적 + 짧은 기간 + 부분 헷지 = 높은 헷지 비율
        ratio1 = hedge_service.calculate_hedge_ratio("PARTIAL", 2, "SHORT")
        assert ratio1 >= 0.5  # 경계값 포함
        
        # 시나리오 2: 공격적 + 긴 기간 + 부분 헷지 = 낮은 헷지 비율
        ratio2 = hedge_service.calculate_hedge_ratio("PARTIAL", 9, "LONG")
        assert ratio2 <= 0.6  # 경계값 포함
        
        # 시나리오 3: 중립 + 중간 기간 + 전체 헷지 = 높은 헷지 비율
        ratio3 = hedge_service.calculate_hedge_ratio("FULL", 5, "MEDIUM")
        assert ratio3 >= 0.7
    
    def test_region_allocation_balance(self):
        """지역별 배분 균형 테스트"""
        allocator = AssetAllocator()
        
        # 다양한 지역 수에 대한 테스트
        for num_regions in [2, 3, 4, 5]:
            regions = ["KOREA", "USA", "EUROPE", "ASIA", "EMERGING"][:num_regions]
            
            result = allocator._calculate_region_allocation(
                preferred_regions=regions,
                home_country="KOREA",
                total_amount=Decimal("100000000")
            )
            
            # 총합이 100%인지 확인
            total_weight = sum(r["weight"] for r in result.values())
            assert abs(total_weight - 1.0) < 0.01
            
            # 본국 비중이 다른 지역보다 높은지 확인 (단, 지역이 2개일 때는 본국 40%, 다른 지역 60%로 나뉠 수 있음)
            if "KOREA" in result and len(result) > 2:
                korea_weight = result["KOREA"]["weight"]
                other_weights = [r["weight"] for r in result.values() if r != result["KOREA"]]
                if other_weights:
                    assert korea_weight >= max(other_weights)


class TestCurrencyHedgeServiceScenarios:
    """환율 헷지 서비스 시나리오 테스트"""
    
    def test_hedge_strategy_recommendations(self):
        """헷지 전략 권장사항 테스트"""
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
            },
            "EUR": {
                "weight": 0.3,
                "amount": 30000000,
                "hedged_amount": 20000000,
                "unhedged_amount": 10000000,
                "hedged": True,
                "hedge_ratio": 0.67
            }
        }
        
        # NONE 헷지 전략
        strategy_none = hedge_service.generate_hedge_strategy(
            currency_allocation=currency_allocation,
            hedge_preference="NONE"
        )
        assert "환율 변동 리스크를 감수" in strategy_none["recommendations"][0]
        
        # PARTIAL 헷지 전략
        strategy_partial = hedge_service.generate_hedge_strategy(
            currency_allocation=currency_allocation,
            hedge_preference="PARTIAL"
        )
        assert "부분 헷지" in strategy_partial["recommendations"][0]
        
        # FULL 헷지 전략
        strategy_full = hedge_service.generate_hedge_strategy(
            currency_allocation=currency_allocation,
            hedge_preference="FULL"
        )
        assert "전체 헷지" in strategy_full["recommendations"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

