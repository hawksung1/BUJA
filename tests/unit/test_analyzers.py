"""
분석기 단위 테스트
"""
import pytest
from datetime import date
from decimal import Decimal
from src.analyzers import (
    AssetAllocator,
    PortfolioAnalyzer,
    PerformanceAnalyzer,
    RiskAnalyzer,
)


class TestAssetAllocator:
    """AssetAllocator 테스트"""
    
    def test_calculate_allocation_conservative(self):
        """보수적 투자 성향 배분 테스트"""
        allocator = AssetAllocator()
        result = allocator.calculate_allocation(risk_tolerance=2)
        
        assert "stock" in result["allocation_percentages"]
        assert result["allocation_percentages"]["stock"] <= 40
        assert result["risk_level"] == "보수적"
    
    def test_calculate_allocation_moderate(self):
        """중립 투자 성향 배분 테스트"""
        allocator = AssetAllocator()
        result = allocator.calculate_allocation(risk_tolerance=5)
        
        assert "stock" in result["allocation_percentages"]
        assert 50 <= result["allocation_percentages"]["stock"] <= 70
        assert result["risk_level"] == "중립"
    
    def test_calculate_allocation_aggressive(self):
        """공격적 투자 성향 배분 테스트"""
        allocator = AssetAllocator()
        result = allocator.calculate_allocation(risk_tolerance=9)
        
        assert "stock" in result["allocation_percentages"]
        assert result["allocation_percentages"]["stock"] >= 60
        assert result["risk_level"] == "공격적"
    
    def test_calculate_allocation_with_amount(self):
        """금액 포함 배분 계산 테스트"""
        allocator = AssetAllocator()
        result = allocator.calculate_allocation(
            risk_tolerance=5,
            total_amount=Decimal("10000000")
        )
        
        assert "allocation_amounts" in result
        assert result["total_amount"] == 10000000.0
        assert sum(result["allocation_amounts"].values()) == pytest.approx(10000000.0, rel=0.01)


class TestPortfolioAnalyzer:
    """PortfolioAnalyzer 테스트"""
    
    def test_calculate_total_value(self):
        """총 자산 가치 계산 테스트"""
        analyzer = PortfolioAnalyzer()
        records = [
            {
                "asset_type": "STOCK",
                "quantity": 10.0,
                "buy_price": 100.0,
                "realized": False
            },
            {
                "asset_type": "BOND",
                "quantity": 5.0,
                "buy_price": 200.0,
                "realized": False
            }
        ]
        
        total = analyzer.calculate_total_value(records)
        assert float(total) == 2000.0  # 10*100 + 5*200
    
    def test_calculate_allocation(self):
        """자산 배분 계산 테스트"""
        analyzer = PortfolioAnalyzer()
        records = [
            {
                "asset_type": "STOCK",
                "quantity": 10.0,
                "buy_price": 100.0,
                "realized": False
            },
            {
                "asset_type": "BOND",
                "quantity": 5.0,
                "buy_price": 200.0,
                "realized": False
            }
        ]
        
        allocation = analyzer.calculate_allocation(records)
        
        assert "STOCK" in allocation
        assert "BOND" in allocation
        assert sum(allocation.values()) == pytest.approx(100.0, rel=0.01)
    
    def test_calculate_diversification_score(self):
        """다각화 점수 계산 테스트"""
        analyzer = PortfolioAnalyzer()
        
        # 단일 자산 (낮은 점수)
        records_single = [
            {"asset_type": "STOCK", "quantity": 10.0, "buy_price": 100.0, "realized": False}
        ]
        score_single = analyzer.calculate_diversification_score(records_single)
        assert score_single < 50
        
        # 다중 자산 (높은 점수)
        records_multi = [
            {"asset_type": "STOCK", "quantity": 5.0, "buy_price": 100.0, "realized": False},
            {"asset_type": "BOND", "quantity": 5.0, "buy_price": 100.0, "realized": False},
            {"asset_type": "CASH", "quantity": 5.0, "buy_price": 100.0, "realized": False}
        ]
        score_multi = analyzer.calculate_diversification_score(records_multi)
        assert score_multi > score_single


class TestPerformanceAnalyzer:
    """PerformanceAnalyzer 테스트"""
    
    def test_calculate_total_return(self):
        """총 수익률 계산 테스트"""
        analyzer = PerformanceAnalyzer()
        records = [
            {
                "asset_type": "STOCK",
                "quantity": 10.0,
                "buy_price": 100.0,
                "realized": False
            }
        ]
        current_prices = {"STOCK": 110.0}  # 10% 상승
        
        result = analyzer.calculate_total_return(records, current_prices)
        
        assert result["total_return_percentage"] == pytest.approx(10.0, rel=0.1)
        assert result["total_profit_loss"] > 0


class TestRiskAnalyzer:
    """RiskAnalyzer 테스트"""
    
    def test_calculate_var(self):
        """VaR 계산 테스트"""
        analyzer = RiskAnalyzer()
        returns = [-0.05, -0.03, 0.01, 0.02, 0.03, 0.05, 0.07]
        
        var = analyzer.calculate_var(returns, 0.95)
        assert var <= 0  # 95% VaR는 보통 음수
    
    def test_calculate_volatility(self):
        """변동성 계산 테스트"""
        analyzer = RiskAnalyzer()
        returns = [0.01, 0.02, -0.01, 0.03, -0.02]
        
        volatility = analyzer.calculate_volatility(returns, annualized=False)
        assert volatility > 0
    
    def test_calculate_max_drawdown(self):
        """최대 낙폭 계산 테스트"""
        analyzer = RiskAnalyzer()
        values = [100, 110, 105, 120, 100, 130]  # 120에서 100으로 낙폭
        
        result = analyzer.calculate_max_drawdown(values)
        
        assert result["max_drawdown"] < 0
        assert result["max_drawdown_percentage"] > 0

