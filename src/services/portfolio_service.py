"""
포트폴리오 관리 서비스
"""
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional

from config.database import Database, db
from config.logging import get_logger
from src.analyzers import (
    PerformanceAnalyzer,
    PortfolioAnalyzer,
    RiskAnalyzer,
)
from src.models import PortfolioAnalysis
from src.repositories import (
    InvestmentRecordRepository,
    PortfolioAnalysisRepository,
)
from src.services.investment_service import InvestmentService
from src.services.user_service import UserService

logger = get_logger(__name__)


class PortfolioService:
    """포트폴리오 관리 서비스"""

    def __init__(self, database: Optional[Database] = None):
        """
        PortfolioService 초기화
        
        Args:
            database: Database 인스턴스 (기본값: 전역 db 인스턴스)
        """
        self.db = database or db
        self.analysis_repo = PortfolioAnalysisRepository(self.db)
        self.record_repo = InvestmentRecordRepository(self.db)
        self.portfolio_analyzer = PortfolioAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.user_service = UserService(self.db)
        self.investment_service = InvestmentService(self.db)

    async def analyze_portfolio(
        self,
        user_id: int,
        current_prices: Optional[Dict[str, Decimal]] = None
    ) -> Dict[str, Any]:
        """
        포트폴리오 종합 분석
        
        Args:
            user_id: 사용자 ID
            current_prices: 현재가 딕셔너리 (선택사항)
        
        Returns:
            분석 결과 딕셔너리
        """
        # 사용자 존재 확인
        await self.user_service.get_user(user_id)

        # 투자 기록 조회
        records = await self.record_repo.get_unrealized(user_id)

        # 딕셔너리로 변환 (공통 유틸리티 사용)
        from src.utils.converters import investment_records_to_dict
        records_dict = investment_records_to_dict(records, include_dates=True)

        # 포트폴리오 분석
        portfolio_analysis = self.portfolio_analyzer.analyze_portfolio(
            records_dict,
            current_prices
        )

        # 성과 분석
        performance_analysis = self.performance_analyzer.calculate_total_return(
            records_dict,
            current_prices
        )

        # 리스크 분석 (수익률 이력이 없으면 기본값)
        risk_analysis = self.risk_analyzer.assess_risk(records_dict)

        result = {
            "portfolio": portfolio_analysis,
            "performance": performance_analysis,
            "risk": risk_analysis,
            "user_id": user_id
        }

        # 분석 결과 저장
        await self._save_analysis(user_id, result)

        logger.info(f"Portfolio analyzed: user_id={user_id}")
        return result

    async def _save_analysis(
        self,
        user_id: int,
        analysis_result: Dict[str, Any]
    ) -> PortfolioAnalysis:
        """
        분석 결과 저장
        
        Args:
            user_id: 사용자 ID
            analysis_result: 분석 결과
        
        Returns:
            저장된 PortfolioAnalysis 객체
        """
        async with self.db.session() as session:
            analysis = PortfolioAnalysis(
                user_id=user_id,
                analysis_date=date.today(),
                total_value=Decimal(str(analysis_result["portfolio"]["total_value"])),
                asset_allocation=analysis_result["portfolio"]["asset_allocation"],
                risk_level=analysis_result["risk"]["risk_level"],
                diversification_score=Decimal(str(analysis_result["portfolio"]["diversification_score"])),
                performance_metrics={
                    "total_return": analysis_result["performance"]["total_return_percentage"],
                    "volatility": analysis_result["risk"]["volatility"],
                    "var_95": analysis_result["risk"]["var_95"],
                    "max_drawdown": analysis_result["risk"]["max_drawdown_percentage"]
                }
            )
            analysis = await self.analysis_repo.create(analysis, session=session)
            await session.commit()
            await session.refresh(analysis)
            return analysis

    async def get_current_allocation(
        self,
        user_id: int
    ) -> Dict[str, float]:
        """
        현재 자산 배분 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            자산 배분 비율 딕셔너리
        """
        records = await self.record_repo.get_unrealized(user_id)

        # 딕셔너리로 변환 (공통 유틸리티 사용)
        from src.utils.converters import investment_records_to_dict
        records_dict = investment_records_to_dict(records, include_dates=False)

        return self.portfolio_analyzer.calculate_allocation(records_dict)

    async def calculate_performance(
        self,
        user_id: int,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        성과 계산
        
        Args:
            user_id: 사용자 ID
            period: 기간 (선택사항)
        
        Returns:
            성과 지표 딕셔너리
        """
        records = await self.record_repo.get_unrealized(user_id)

        # 딕셔너리로 변환 (공통 유틸리티 사용)
        from src.utils.converters import investment_records_to_dict
        records_dict = investment_records_to_dict(records, include_dates=True, include_sell_price=True)

        performance = self.performance_analyzer.calculate_total_return(records_dict)
        annualized = self.performance_analyzer.calculate_annualized_return(records_dict)

        return {
            "total_return": float(performance["total_return_percentage"]),
            "annualized_return": float(annualized),
            "total_profit_loss": float(performance["total_profit_loss"]),
            "realized_profit": float(performance["realized_profit"])
        }

    async def get_rebalancing_suggestion(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        리밸런싱 제안
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            리밸런싱 제안 딕셔너리
        """
        # 현재 배분
        current_allocation = await self.get_current_allocation(user_id)

        # 목표 배분 (투자 성향 기반, 추후 구현)
        # 여기서는 간단히 현재 배분을 기준으로 제안

        return {
            "current_allocation": current_allocation,
            "target_allocation": current_allocation,  # TODO: 투자 성향 기반 계산
            "suggestions": []
        }

    async def get_portfolio_summary(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get portfolio summary for dashboard
        
        Args:
            user_id: User ID
        
        Returns:
            Portfolio summary dictionary
        """
        try:
            # Get investment records
            records = await self.record_repo.get_unrealized(user_id)

            if not records:
                return {
                    "total_value": 0,
                    "total_return": 0,
                    "asset_count": 0
                }

            # Calculate total value and return (공통 유틸리티 사용)
            from src.utils.converters import investment_records_to_dict
            records_dict = investment_records_to_dict(records, include_dates=False)

            portfolio_analysis = self.portfolio_analyzer.analyze_portfolio(records_dict)
            performance = self.performance_analyzer.calculate_total_return(records_dict)

            return {
                "total_value": float(portfolio_analysis.get("total_value", 0)),
                "total_return": float(performance.get("total_return_percentage", 0)),
                "asset_count": len(records)
            }
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {
                "total_value": 0,
                "total_return": 0,
                "asset_count": 0
            }

