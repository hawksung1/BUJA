"""
환율 헷지 서비스
"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
from config.logging import get_logger

logger = get_logger(__name__)


class CurrencyHedgeService:
    """환율 헷지 전략 서비스"""
    
    # 주요 통화 코드
    CURRENCIES = {
        "KOREA": "KRW",
        "USA": "USD",
        "JAPAN": "JPY",
        "CHINA": "CNY",
        "EUROPE": "EUR",
        "SINGAPORE": "SGD",
        "OTHER": "USD"  # 기본값
    }
    
    # 지역별 통화 매핑
    REGION_CURRENCIES = {
        "KOREA": ["KRW"],
        "USA": ["USD"],
        "EUROPE": ["EUR", "GBP", "CHF"],
        "ASIA": ["JPY", "CNY", "SGD", "HKD", "KRW"],
        "EMERGING": ["BRL", "MXN", "INR", "ZAR", "TRY"],
        "GLOBAL": ["USD", "EUR", "JPY", "GBP", "CNY"]
    }
    
    def calculate_hedge_ratio(
        self,
        hedge_preference: str,
        risk_tolerance: int,
        investment_period: Optional[str] = None
    ) -> float:
        """
        환율 헷지 비율 계산
        
        Args:
            hedge_preference: 헷지 선호도 (NONE, PARTIAL, FULL)
            risk_tolerance: 위험 감수 성향 (1-10)
            investment_period: 투자 기간 (SHORT, MEDIUM, LONG)
        
        Returns:
            헷지 비율 (0.0 ~ 1.0)
        """
        if hedge_preference == "NONE":
            return 0.0
        elif hedge_preference == "FULL":
            # FULL인 경우에도 위험 감수 성향에 따라 조정
            base_ratio = 0.9
            # 위험 감수 성향이 높을수록 헷지 비율 감소
            adjustment = (risk_tolerance - 5) * 0.05  # -0.2 ~ +0.2
            return max(0.7, min(1.0, base_ratio + adjustment))
        else:  # PARTIAL
            # 기본 50% 헷지, 위험 감수 성향과 투자 기간에 따라 조정
            base_ratio = 0.5
            
            # 위험 감수 성향 조정 (높을수록 헷지 비율 감소)
            risk_adjustment = (risk_tolerance - 5) * 0.05  # -0.2 ~ +0.2
            
            # 투자 기간 조정 (짧을수록 헷지 비율 증가)
            period_adjustment = 0.0
            if investment_period == "SHORT":
                period_adjustment = 0.15
            elif investment_period == "MEDIUM":
                period_adjustment = 0.0
            elif investment_period == "LONG":
                period_adjustment = -0.1
            
            final_ratio = base_ratio + risk_adjustment + period_adjustment
            return max(0.3, min(0.8, final_ratio))
    
    def calculate_currency_allocation(
        self,
        preferred_regions: List[str],
        home_country: str,
        total_amount: Decimal,
        hedge_ratio: float
    ) -> Dict[str, Dict[str, Any]]:
        """
        통화별 자산 배분 계산
        
        Args:
            preferred_regions: 선호 투자 지역 리스트
            home_country: 거주 국가
            total_amount: 총 투자 금액
            hedge_ratio: 헷지 비율
        
        Returns:
            통화별 배분 딕셔너리
        """
        home_currency = self.CURRENCIES.get(home_country, "KRW")
        
        # 지역별 통화 수집
        currencies = set()
        currencies.add(home_currency)  # 본국 통화는 항상 포함
        
        for region in preferred_regions:
            if region in self.REGION_CURRENCIES:
                currencies.update(self.REGION_CURRENCIES[region])
        
        # 본국 통화 비중 계산 (헷지 비율에 따라 조정)
        home_currency_weight = 0.3 + (hedge_ratio * 0.3)  # 30% ~ 60%
        
        # 나머지 통화에 균등 분배
        other_currencies = list(currencies - {home_currency})
        remaining_weight = 1.0 - home_currency_weight
        
        if not other_currencies:
            # 본국 통화만 있는 경우
            return {
                home_currency: {
                    "weight": 1.0,
                    "amount": float(total_amount),
                    "hedged": False
                }
            }
        
        # 각 통화별 가중치 계산
        currency_weights = {}
        weight_per_currency = remaining_weight / len(other_currencies)
        
        currency_weights[home_currency] = home_currency_weight
        
        for currency in other_currencies:
            currency_weights[currency] = weight_per_currency
        
        # 헷지 적용
        result = {}
        for currency, weight in currency_weights.items():
            is_hedged = currency != home_currency and hedge_ratio > 0
            hedged_amount = float(total_amount) * weight * (hedge_ratio if is_hedged else 1.0)
            unhedged_amount = float(total_amount) * weight * (1.0 - hedge_ratio) if is_hedged else 0.0
            
            result[currency] = {
                "weight": weight,
                "amount": float(total_amount) * weight,
                "hedged_amount": hedged_amount,
                "unhedged_amount": unhedged_amount,
                "hedged": is_hedged,
                "hedge_ratio": hedge_ratio if is_hedged else 0.0
            }
        
        return result
    
    def generate_hedge_strategy(
        self,
        currency_allocation: Dict[str, Dict[str, Any]],
        hedge_preference: str
    ) -> Dict[str, Any]:
        """
        환율 헷지 전략 생성
        
        Args:
            currency_allocation: 통화별 배분
            hedge_preference: 헷지 선호도
        
        Returns:
            헷지 전략 딕셔너리
        """
        total_hedged = sum(
            alloc["hedged_amount"] 
            for alloc in currency_allocation.values() 
            if alloc.get("hedged", False)
        )
        
        total_unhedged = sum(
            alloc["unhedged_amount"] 
            for alloc in currency_allocation.values() 
            if alloc.get("hedged", False)
        )
        
        strategy = {
            "hedge_preference": hedge_preference,
            "total_hedged_amount": total_hedged,
            "total_unhedged_amount": total_unhedged,
            "hedge_ratio": total_hedged / (total_hedged + total_unhedged) if (total_hedged + total_unhedged) > 0 else 0.0,
            "currency_breakdown": currency_allocation,
            "recommendations": []
        }
        
        # 권장사항 생성
        if hedge_preference == "NONE":
            strategy["recommendations"].append(
                "환율 변동 리스크를 감수하고 있습니다. 환율 변동에 주의하세요."
            )
        elif hedge_preference == "PARTIAL":
            strategy["recommendations"].append(
                "부분 헷지로 환율 리스크와 수익 기회의 균형을 맞추고 있습니다."
            )
            strategy["recommendations"].append(
                "정기적으로 환율 변동을 모니터링하고 필요시 헷지 비율을 조정하세요."
            )
        else:  # FULL
            strategy["recommendations"].append(
                "전체 헷지로 환율 변동 리스크를 최소화하고 있습니다."
            )
            strategy["recommendations"].append(
                "헷지 비용을 고려하여 장기적으로는 부분 헷지로 전환을 검토하세요."
            )
        
        return strategy

