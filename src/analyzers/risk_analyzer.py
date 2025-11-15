"""
리스크 분석기
"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import date, datetime
import numpy as np
from config.logging import get_logger

logger = get_logger(__name__)


class RiskAnalyzer:
    """리스크 분석기"""
    
    def calculate_var(
        self,
        returns: List[float],
        confidence_level: float = 0.95
    ) -> float:
        """
        VaR (Value at Risk) 계산
        
        Args:
            returns: 수익률 리스트
            confidence_level: 신뢰 수준 (기본값: 0.95 = 95%)
        
        Returns:
            VaR 값
        """
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence_level) * 100)
        
        return float(var)
    
    def calculate_cvar(
        self,
        returns: List[float],
        confidence_level: float = 0.95
    ) -> float:
        """
        CVaR (Conditional VaR) 계산
        
        Args:
            returns: 수익률 리스트
            confidence_level: 신뢰 수준 (기본값: 0.95 = 95%)
        
        Returns:
            CVaR 값
        """
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        var = self.calculate_var(returns, confidence_level)
        
        # VaR보다 낮은 수익률의 평균
        tail_returns = returns_array[returns_array <= var]
        cvar = np.mean(tail_returns) if len(tail_returns) > 0 else var
        
        return float(cvar)
    
    def calculate_volatility(
        self,
        returns: List[float],
        annualized: bool = True
    ) -> float:
        """
        포트폴리오 변동성 계산
        
        Args:
            returns: 수익률 리스트
            annualized: 연환산 여부
        
        Returns:
            변동성 (표준편차)
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        volatility = np.std(returns_array, ddof=1)
        
        if annualized:
            # 연환산 (일일 수익률 기준으로 가정)
            volatility *= np.sqrt(252)  # 거래일 기준
        
        return float(volatility)
    
    def calculate_beta(
        self,
        portfolio_returns: List[float],
        market_returns: List[float]
    ) -> float:
        """
        베타 계산 (시장 대비 변동성)
        
        Args:
            portfolio_returns: 포트폴리오 수익률 리스트
            market_returns: 시장 수익률 리스트
        
        Returns:
            베타 값
        """
        if len(portfolio_returns) != len(market_returns) or len(portfolio_returns) < 2:
            return 1.0  # 기본값
        
        portfolio_array = np.array(portfolio_returns)
        market_array = np.array(market_returns)
        
        # 공분산과 분산 계산
        covariance = np.cov(portfolio_array, market_array)[0, 1]
        market_variance = np.var(market_array, ddof=1)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        return float(beta)
    
    def calculate_max_drawdown(
        self,
        values: List[float]
    ) -> Dict[str, float]:
        """
        최대 낙폭 (Maximum Drawdown) 계산
        
        Args:
            values: 자산 가치 리스트 (시간순)
        
        Returns:
            최대 낙폭 정보 딕셔너리
        """
        if not values or len(values) < 2:
            return {
                "max_drawdown": 0.0,
                "max_drawdown_percentage": 0.0
            }
        
        values_array = np.array(values)
        peak = np.maximum.accumulate(values_array)
        drawdown = (values_array - peak) / peak
        max_drawdown = np.min(drawdown)
        max_drawdown_percentage = abs(max_drawdown) * 100
        
        return {
            "max_drawdown": float(max_drawdown),
            "max_drawdown_percentage": float(max_drawdown_percentage)
        }
    
    def assess_risk(
        self,
        investment_records: List[Dict[str, Any]],
        returns_history: Optional[List[float]] = None,
        market_returns: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        포트폴리오 리스크 평가
        
        Args:
            investment_records: 투자 기록 리스트
            returns_history: 수익률 이력 (선택사항)
            market_returns: 시장 수익률 이력 (선택사항)
        
        Returns:
            리스크 평가 결과 딕셔너리
        """
        if not returns_history:
            # 수익률 이력이 없으면 기본값 반환
            return {
                "var_95": 0.0,
                "cvar_95": 0.0,
                "volatility": 0.0,
                "beta": 1.0,
                "max_drawdown": 0.0,
                "risk_level": "LOW"
            }
        
        var_95 = self.calculate_var(returns_history, 0.95)
        cvar_95 = self.calculate_cvar(returns_history, 0.95)
        volatility = self.calculate_volatility(returns_history)
        
        beta = 1.0
        if market_returns:
            beta = self.calculate_beta(returns_history, market_returns)
        
        # 가치 이력 생성 (간단한 추정)
        values = []
        cumulative_return = 1.0
        for ret in returns_history:
            cumulative_return *= (1 + ret)
            values.append(cumulative_return)
        
        max_dd = self.calculate_max_drawdown(values)
        
        # 위험 수준 판정
        if volatility < 0.1:
            risk_level = "LOW"
        elif volatility < 0.2:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            "var_95": var_95,
            "cvar_95": cvar_95,
            "volatility": volatility,
            "beta": beta,
            "max_drawdown": max_dd["max_drawdown"],
            "max_drawdown_percentage": max_dd["max_drawdown_percentage"],
            "risk_level": risk_level
        }
    
    async def calculate_risk(
        self,
        portfolio_data: Dict[str, Any],
        risk_metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        포트폴리오 리스크 계산 (Tool용)
        
        Args:
            portfolio_data: 포트폴리오 데이터 (자산 유형별 비중 등)
            risk_metrics: 계산할 리스크 지표 목록 (var, sharpe, max_drawdown 등)
        
        Returns:
            리스크 지표 딕셔너리
        """
        if risk_metrics is None:
            risk_metrics = ["var", "sharpe", "max_drawdown"]
        
        result = {}
        
        # 포트폴리오 데이터에서 수익률 이력 추출 (간단한 시뮬레이션)
        # 실제로는 과거 데이터가 필요하지만, 여기서는 기본값 사용
        returns_history = portfolio_data.get("returns_history", [])
        
        if "var" in risk_metrics:
            if returns_history:
                result["var_95"] = self.calculate_var(returns_history, 0.95)
                result["var_99"] = self.calculate_var(returns_history, 0.99)
            else:
                result["var_95"] = 0.0
                result["var_99"] = 0.0
        
        if "cvar" in risk_metrics or "expected_shortfall" in risk_metrics:
            if returns_history:
                result["cvar_95"] = self.calculate_cvar(returns_history, 0.95)
            else:
                result["cvar_95"] = 0.0
        
        if "volatility" in risk_metrics:
            if returns_history:
                result["volatility"] = self.calculate_volatility(returns_history)
            else:
                result["volatility"] = 0.0
        
        if "sharpe" in risk_metrics:
            # Sharpe Ratio 계산 (간단한 버전)
            if returns_history and len(returns_history) > 0:
                mean_return = np.mean(returns_history)
                volatility = self.calculate_volatility(returns_history)
                risk_free_rate = portfolio_data.get("risk_free_rate", 0.02)  # 기본값 2%
                if volatility > 0:
                    result["sharpe_ratio"] = (mean_return - risk_free_rate) / volatility
                else:
                    result["sharpe_ratio"] = 0.0
            else:
                result["sharpe_ratio"] = 0.0
        
        if "max_drawdown" in risk_metrics:
            if returns_history:
                values = []
                cumulative_return = 1.0
                for ret in returns_history:
                    cumulative_return *= (1 + ret)
                    values.append(cumulative_return)
                max_dd = self.calculate_max_drawdown(values)
                result["max_drawdown"] = max_dd["max_drawdown"]
                result["max_drawdown_percentage"] = max_dd["max_drawdown_percentage"]
            else:
                result["max_drawdown"] = 0.0
                result["max_drawdown_percentage"] = 0.0
        
        if "beta" in risk_metrics:
            market_returns = portfolio_data.get("market_returns", [])
            if returns_history and market_returns:
                result["beta"] = self.calculate_beta(returns_history, market_returns)
            else:
                result["beta"] = 1.0
        
        return result

