"""
포트폴리오 분석기
"""
import math
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from config.logging import get_logger

logger = get_logger(__name__)


class PortfolioAnalyzer:
    """포트폴리오 분석기"""

    def calculate_total_value(
        self,
        investment_records: List[Dict[str, Any]],
        current_prices: Optional[Dict[str, Decimal]] = None
    ) -> Decimal:
        """
        총 자산 가치 계산
        
        Args:
            investment_records: 투자 기록 리스트
            current_prices: 현재가 딕셔너리 (symbol -> price, 선택사항)
        
        Returns:
            총 자산 가치
        """
        total = Decimal("0")

        for record in investment_records:
            if record.get("realized", False):
                continue  # 실현된 기록은 제외

            quantity = Decimal(str(record.get("quantity", 0)))

            # 현재가가 있으면 현재가 기준, 없으면 매수가 기준
            if current_prices and record.get("symbol"):
                price = current_prices.get(record["symbol"], record.get("buy_price", 0))
            else:
                price = Decimal(str(record.get("buy_price", 0)))

            total += quantity * price

        return total

    def calculate_allocation(
        self,
        investment_records: List[Dict[str, Any]],
        current_prices: Optional[Dict[str, Decimal]] = None
    ) -> Dict[str, float]:
        """
        자산 배분 비율 계산
        
        Args:
            investment_records: 투자 기록 리스트
            current_prices: 현재가 딕셔너리 (선택사항)
        
        Returns:
            자산 유형별 배분 비율 딕셔너리
        """
        total_value = self.calculate_total_value(investment_records, current_prices)

        if total_value == 0:
            return {}

        allocation = {}

        for record in investment_records:
            if record.get("realized", False):
                continue

            asset_type = record.get("asset_type", "UNKNOWN")
            quantity = Decimal(str(record.get("quantity", 0)))

            if current_prices and record.get("symbol"):
                price = current_prices.get(record["symbol"], record.get("buy_price", 0))
            else:
                price = Decimal(str(record.get("buy_price", 0)))

            value = quantity * price
            percentage = (value / total_value) * 100

            if asset_type not in allocation:
                allocation[asset_type] = 0
            allocation[asset_type] += float(percentage)

        return allocation

    def calculate_diversification_score(
        self,
        investment_records: List[Dict[str, Any]],
        current_prices: Optional[Dict[str, Decimal]] = None
    ) -> float:
        """
        다각화 점수 계산 (0-100)
        
        Args:
            investment_records: 투자 기록 리스트
            current_prices: 현재가 딕셔너리 (선택사항)
        
        Returns:
            다각화 점수 (0-100)
        """
        allocation = self.calculate_allocation(investment_records, current_prices)

        if not allocation:
            return 0.0

        # 자산 유형 수 기반 점수 (최대 50점)
        asset_type_count = len(allocation)
        type_score = min(50, asset_type_count * 10)

        # 자산 분산도 기반 점수 (최대 50점)
        # 엔트로피 기반 계산
        total = sum(allocation.values())
        if total == 0:
            return 0.0

        entropy = 0
        for percentage in allocation.values():
            if percentage > 0:
                p = percentage / total
                entropy -= p * math.log2(p)

        # 정규화 (0-50점)
        max_entropy = math.log2(len(allocation)) if len(allocation) > 1 else 1
        entropy_score = min(50, (entropy / max_entropy) * 50) if max_entropy > 0 else 0

        return type_score + entropy_score

    def analyze_portfolio(
        self,
        investment_records: List[Dict[str, Any]],
        current_prices: Optional[Dict[str, Decimal]] = None
    ) -> Dict[str, Any]:
        """
        포트폴리오 종합 분석
        
        Args:
            investment_records: 투자 기록 리스트
            current_prices: 현재가 딕셔너리 (선택사항)
        
        Returns:
            분석 결과 딕셔너리
        """
        total_value = self.calculate_total_value(investment_records, current_prices)
        allocation = self.calculate_allocation(investment_records, current_prices)
        diversification_score = self.calculate_diversification_score(investment_records, current_prices)

        return {
            "total_value": float(total_value),
            "asset_allocation": allocation,
            "diversification_score": diversification_score,
            "record_count": len([r for r in investment_records if not r.get("realized", False)]),
            "analysis_date": datetime.now().isoformat()
        }

