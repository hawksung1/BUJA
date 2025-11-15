"""
성과 분석기
"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import date, datetime, timedelta
import math
from config.logging import get_logger

logger = get_logger(__name__)


class PerformanceAnalyzer:
    """성과 분석기"""
    
    def calculate_total_return(
        self,
        investment_records: List[Dict[str, Any]],
        current_prices: Optional[Dict[str, Decimal]] = None
    ) -> Dict[str, Decimal]:
        """
        총 수익률 계산
        
        Args:
            investment_records: 투자 기록 리스트
            current_prices: 현재가 딕셔너리 (선택사항)
        
        Returns:
            수익률 통계 딕셔너리
        """
        total_cost = Decimal("0")
        total_value = Decimal("0")
        realized_profit = Decimal("0")
        
        for record in investment_records:
            quantity = Decimal(str(record.get("quantity", 0)))
            buy_price = Decimal(str(record.get("buy_price", 0)))
            cost = quantity * buy_price
            total_cost += cost
            
            if record.get("realized", False):
                # 실현된 기록
                sell_price = Decimal(str(record.get("sell_price", 0)))
                value = quantity * sell_price
                total_value += value
                profit = (sell_price - buy_price) * quantity
                realized_profit += profit
            else:
                # 미실현 기록
                if current_prices and record.get("symbol"):
                    current_price = current_prices.get(record["symbol"], buy_price)
                else:
                    current_price = buy_price
                value = quantity * current_price
                total_value += value
        
        # 총 수익률
        if total_cost > 0:
            total_return = ((total_value - total_cost) / total_cost) * 100
        else:
            total_return = Decimal("0")
        
        return {
            "total_cost": total_cost,
            "total_value": total_value,
            "total_profit_loss": total_value - total_cost,
            "total_return_percentage": total_return,
            "realized_profit": realized_profit
        }
    
    def calculate_annualized_return(
        self,
        investment_records: List[Dict[str, Any]],
        current_prices: Optional[Dict[str, Decimal]] = None,
        end_date: Optional[date] = None
    ) -> Decimal:
        """
        연환산 수익률 계산
        
        Args:
            investment_records: 투자 기록 리스트
            current_prices: 현재가 딕셔너리 (선택사항)
            end_date: 종료일 (기본값: 오늘)
        
        Returns:
            연환산 수익률 (%)
        """
        if not investment_records:
            return Decimal("0")
        
        end_date = end_date or date.today()
        
        # 가장 오래된 투자 기록 찾기
        oldest_date = min(
            record.get("buy_date", end_date)
            for record in investment_records
            if not record.get("realized", False)
        )
        
        if isinstance(oldest_date, str):
            oldest_date = datetime.fromisoformat(oldest_date).date()
        
        # 투자 기간 계산 (년)
        days = (end_date - oldest_date).days
        if days <= 0:
            return Decimal("0")
        
        years = days / 365.25
        
        # 총 수익률 계산
        returns = self.calculate_total_return(investment_records, current_prices)
        total_return = returns["total_return_percentage"] / 100  # 소수로 변환
        
        # 연환산 수익률 = (1 + 총수익률)^(1/년수) - 1
        if total_return > -1:  # -100% 이상
            annualized = ((1 + float(total_return)) ** (1 / years) - 1) * 100
        else:
            annualized = Decimal("-100")  # -100% 이하는 -100%로 제한
        
        return Decimal(str(annualized))
    
    def compare_with_benchmark(
        self,
        portfolio_return: Decimal,
        benchmark_return: Decimal
    ) -> Dict[str, Any]:
        """
        벤치마크 대비 성과 비교
        
        Args:
            portfolio_return: 포트폴리오 수익률 (%)
            benchmark_return: 벤치마크 수익률 (%)
        
        Returns:
            비교 결과 딕셔너리
        """
        excess_return = portfolio_return - benchmark_return
        
        return {
            "portfolio_return": float(portfolio_return),
            "benchmark_return": float(benchmark_return),
            "excess_return": float(excess_return),
            "outperformance": excess_return > 0
        }
    
    def analyze_by_asset_type(
        self,
        investment_records: List[Dict[str, Any]],
        current_prices: Optional[Dict[str, Decimal]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        자산 유형별 성과 분석
        
        Args:
            investment_records: 투자 기록 리스트
            current_prices: 현재가 딕셔너리 (선택사항)
        
        Returns:
            자산 유형별 성과 딕셔너리
        """
        asset_type_records: Dict[str, List[Dict[str, Any]]] = {}
        
        for record in investment_records:
            asset_type = record.get("asset_type", "UNKNOWN")
            if asset_type not in asset_type_records:
                asset_type_records[asset_type] = []
            asset_type_records[asset_type].append(record)
        
        results = {}
        for asset_type, records in asset_type_records.items():
            returns = self.calculate_total_return(records, current_prices)
            results[asset_type] = {
                "record_count": len(records),
                "total_cost": float(returns["total_cost"]),
                "total_value": float(returns["total_value"]),
                "total_return_percentage": float(returns["total_return_percentage"]),
                "profit_loss": float(returns["total_profit_loss"])
            }
        
        return results

