"""
포트폴리오 모니터링 시나리오 통합 테스트
USER_SCENARIO.md의 6단계(정기 상담 및 포트폴리오 모니터링)와 7단계(장기 모니터링 및 전략 조정)를 테스트
"""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from src.models import (
    AssetType,
    InvestmentPeriod,
    InvestmentExperience,
    GoalType,
)
from src.services.investment_preference_service import InvestmentPreferenceService
from src.services.investment_service import InvestmentService
from src.services.portfolio_service import PortfolioService
from src.services.recommendation_service import RecommendationService
from src.services.user_service import UserService


class TestPortfolioMonitoringScenarios:
    """포트폴리오 모니터링 시나리오 테스트"""

    @pytest.fixture
    def setup_user_with_portfolio(self, db_session):
        """포트폴리오를 가진 사용자 설정"""
        # 사용자 생성
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="monitoring_test@example.com",
            password="testpass123",
            name="김철수",
            age=32,
            occupation="IT 개발자"
        )

        # 투자 성향 설정
        pref_service = InvestmentPreferenceService(db_session)
        preference = pref_service.create_or_update_preference(
            user_id=user.id,
            risk_tolerance=5,
            target_return=8.0,
            investment_period=InvestmentPeriod.MEDIUM,
            investment_experience=InvestmentExperience.BEGINNER,
            max_loss_tolerance=15.0,
            preferred_assets=[AssetType.STOCK, AssetType.ETF]
        )

        # 재무 목표 설정 (주택 구매)
        from src.services.financial_goal_service import FinancialGoalService
        goal_service = FinancialGoalService(db_session)
        goal = goal_service.create_goal(
            user_id=user.id,
            goal_type=GoalType.HOUSE,
            target_amount=Decimal("300000000"),  # 3억원
            target_date=datetime.now() + timedelta(days=365*5),  # 5년 후
            priority=1
        )

        # 투자 내역 추가 (1개월 전 투자)
        investment_service = InvestmentService(db_session)
        one_month_ago = datetime.now() - timedelta(days=30)
        
        investments = [
            # 채권형 ETF (40%)
            {
                "asset_name": "KODEX 국고채3년",
                "asset_type": AssetType.ETF,
                "amount": Decimal("360000"),
                "purchase_price": Decimal("10000"),
                "current_price": Decimal("10050"),
                "purchase_date": one_month_ago
            },
            {
                "asset_name": "KODEX 미국채권",
                "asset_type": AssetType.ETF,
                "amount": Decimal("360000"),
                "purchase_price": Decimal("10000"),
                "current_price": Decimal("10080"),
                "purchase_date": one_month_ago
            },
            # 주식형 ETF (60%)
            {
                "asset_name": "KODEX 200",
                "asset_type": AssetType.ETF,
                "amount": Decimal("450000"),
                "purchase_price": Decimal("10000"),
                "current_price": Decimal("10150"),
                "purchase_date": one_month_ago
            },
            {
                "asset_name": "KODEX 미국S&P500",
                "asset_type": AssetType.ETF,
                "amount": Decimal("360000"),
                "purchase_price": Decimal("10000"),
                "current_price": Decimal("10200"),
                "purchase_date": one_month_ago
            },
            {
                "asset_name": "KODEX 나스닥100",
                "asset_type": AssetType.ETF,
                "amount": Decimal("270000"),
                "purchase_price": Decimal("10000"),
                "current_price": Decimal("10250"),
                "purchase_date": one_month_ago
            }
        ]

        for inv_data in investments:
            investment_service.create_investment(
                user_id=user.id,
                asset_name=inv_data["asset_name"],
                asset_type=inv_data["asset_type"],
                amount=inv_data["amount"],
                purchase_price=inv_data["purchase_price"],
                current_price=inv_data["current_price"],
                purchase_date=inv_data["purchase_date"]
            )

        return user, preference, goal

    def test_scenario_1_month_monitoring(self, db_session, setup_user_with_portfolio):
        """시나리오 6.1: 1개월 후 상담
        
        - 총 투자액: 180만원
        - 현재 평가액: 약 182만원
        - 수익률: +1.1%
        - 투자 기간: 1개월
        """
        user, preference, goal = setup_user_with_portfolio

        # 포트폴리오 분석
        portfolio_service = PortfolioService(db_session)
        portfolio_summary = portfolio_service.get_portfolio_summary(user.id)

        # 검증
        assert portfolio_summary is not None
        assert "total_value" in portfolio_summary
        assert "total_return_rate" in portfolio_summary

        # 총 투자액 확인 (180만원)
        total_invested = Decimal("1800000")
        assert abs(portfolio_summary["total_invested"] - total_invested) < Decimal("1000")

        # 수익률 확인 (약 1.1%)
        return_rate = portfolio_summary["total_return_rate"]
        assert 0.5 <= return_rate <= 2.0, f"수익률이 예상 범위를 벗어남: {return_rate}%"

        # 자산별 성과 확인
        assert "assets" in portfolio_summary
        assets = portfolio_summary["assets"]
        assert len(assets) == 5

        # 채권형 ETF 성과 확인 (안정적)
        bond_etfs = [a for a in assets if "국고채" in a["asset_name"] or "채권" in a["asset_name"]]
        for bond_etf in bond_etfs:
            assert bond_etf["return_rate"] >= 0, "채권형 ETF 손실 발생"

        # 주식형 ETF 성과 확인 (우수)
        stock_etfs = [a for a in assets if "200" in a["asset_name"] or "S&P" in a["asset_name"] or "나스닥" in a["asset_name"]]
        for stock_etf in stock_etfs:
            assert stock_etf["return_rate"] >= 0.5, "주식형 ETF 성과 부진"

        print("[✅] 1개월 후 포트폴리오 모니터링 성공")

    def test_scenario_6_month_monitoring(self, db_session, setup_user_with_portfolio):
        """시나리오 7.1: 6개월 후 상담
        
        - 총 투자액: 1,080만원 (월 180만원 × 6개월)
        - 현재 평가액: 약 1,150만원
        - 수익률: +6.5%
        - 연환산 수익률: 약 13%
        """
        user, preference, goal = setup_user_with_portfolio

        # 6개월간 투자 시뮬레이션 (매월 180만원 투자)
        investment_service = InvestmentService(db_session)
        
        for month in range(1, 6):  # 1~5개월 추가 (0개월은 이미 설정됨)
            investment_date = datetime.now() - timedelta(days=30*(6-month))
            
            # 매월 동일한 비율로 투자
            monthly_investments = [
                ("KODEX 국고채3년", AssetType.ETF, Decimal("360000")),
                ("KODEX 미국채권", AssetType.ETF, Decimal("360000")),
                ("KODEX 200", AssetType.ETF, Decimal("450000")),
                ("KODEX 미국S&P500", AssetType.ETF, Decimal("360000")),
                ("KODEX 나스닥100", AssetType.ETF, Decimal("270000"))
            ]
            
            for asset_name, asset_type, amount in monthly_investments:
                # 시간이 지날수록 가격 상승 시뮬레이션
                price_increase = 1 + (month * 0.01)  # 월 1% 상승
                current_price = Decimal("10000") * Decimal(str(price_increase))
                
                investment_service.create_investment(
                    user_id=user.id,
                    asset_name=asset_name,
                    asset_type=asset_type,
                    amount=amount,
                    purchase_price=Decimal("10000"),
                    current_price=current_price,
                    purchase_date=investment_date
                )

        # 포트폴리오 분석
        portfolio_service = PortfolioService(db_session)
        portfolio_summary = portfolio_service.get_portfolio_summary(user.id)

        # 검증
        assert portfolio_summary is not None

        # 총 투자액 확인 (1,080만원)
        total_invested = Decimal("10800000")
        assert abs(portfolio_summary["total_invested"] - total_invested) < Decimal("10000")

        # 수익률 확인 (약 6.5%)
        return_rate = portfolio_summary["total_return_rate"]
        assert 5.0 <= return_rate <= 8.0, f"수익률이 예상 범위를 벗어남: {return_rate}%"

        # 리스크 분석
        risk_metrics = portfolio_service.calculate_risk_metrics(user.id)
        assert "volatility" in risk_metrics
        assert "max_drawdown" in risk_metrics

        # 최대 낙폭 확인 (허용 범위 내)
        max_drawdown = risk_metrics["max_drawdown"]
        assert max_drawdown <= 15.0, f"최대 낙폭이 허용 범위를 초과: {max_drawdown}%"

        print("[✅] 6개월 후 포트폴리오 모니터링 성공")

    def test_scenario_rebalancing_recommendation(self, db_session, setup_user_with_portfolio):
        """리밸런싱 추천 시나리오 테스트
        
        - 포트폴리오 비중이 계획에서 벗어났을 때 리밸런싱 추천
        - 목표 비중: 채권 40%, 주식 60%
        """
        user, preference, goal = setup_user_with_portfolio

        # 포트폴리오 서비스
        portfolio_service = PortfolioService(db_session)
        
        # 현재 포트폴리오 비중 확인
        allocation = portfolio_service.get_asset_allocation(user.id)
        
        assert "bond" in allocation or "etf" in allocation
        assert "stock" in allocation or "etf" in allocation

        # 리밸런싱 필요 여부 확인
        rebalancing_needed = portfolio_service.check_rebalancing_needed(
            user_id=user.id,
            target_allocation={"bond": 40, "stock": 60}
        )

        # 리밸런싱이 필요한 경우 추천 생성
        if rebalancing_needed:
            recommendation_service = RecommendationService(db_session)
            rebalancing_plan = recommendation_service.generate_rebalancing_plan(
                user_id=user.id,
                target_allocation={"bond": 40, "stock": 60}
            )

            assert rebalancing_plan is not None
            assert "actions" in rebalancing_plan
            assert len(rebalancing_plan["actions"]) > 0

            print("[✅] 리밸런싱 추천 생성 성공")
        else:
            print("[✅] 리밸런싱 불필요 - 포트폴리오 비중 유지")

    def test_scenario_goal_progress_tracking(self, db_session, setup_user_with_portfolio):
        """재무 목표 진행률 추적 시나리오 테스트
        
        - 목표: 주택 구매 3억원 (5년 후)
        - 현재 자산: 포트폴리오 평가액
        - 진행률 계산
        """
        user, preference, goal = setup_user_with_portfolio

        # 포트폴리오 평가액 확인
        portfolio_service = PortfolioService(db_session)
        portfolio_summary = portfolio_service.get_portfolio_summary(user.id)

        current_value = portfolio_summary["total_value"]

        # 목표 진행률 계산
        target_amount = Decimal("300000000")  # 3억원
        progress_rate = (current_value / target_amount) * 100

        assert progress_rate >= 0
        assert progress_rate <= 100

        # 목표 달성 예상 시뮬레이션
        from src.services.financial_goal_service import FinancialGoalService
        goal_service = FinancialGoalService(db_session)
        
        projection = goal_service.project_goal_achievement(
            user_id=user.id,
            goal_id=goal.id,
            monthly_investment=Decimal("1800000"),  # 월 180만원
            expected_return_rate=9.0  # 연 9%
        )

        assert "projected_value" in projection
        assert "achievement_probability" in projection

        print(f"[✅] 목표 진행률: {progress_rate:.2f}%")
        print(f"[✅] 목표 달성 예상: {projection['achievement_probability']:.2f}%")

    def test_scenario_performance_report(self, db_session, setup_user_with_portfolio):
        """성과 리포트 생성 시나리오 테스트
        
        - 월별/연별 성과 리포트 생성
        - 주요 지표: 수익률, 리스크, 샤프 비율 등
        """
        user, preference, goal = setup_user_with_portfolio

        # 포트폴리오 서비스
        portfolio_service = PortfolioService(db_session)

        # 성과 리포트 생성
        performance_report = portfolio_service.generate_performance_report(
            user_id=user.id,
            period="monthly"  # 월별 리포트
        )

        # 검증
        assert performance_report is not None
        assert "period" in performance_report
        assert "total_return" in performance_report
        assert "risk_metrics" in performance_report

        # 주요 지표 확인
        risk_metrics = performance_report["risk_metrics"]
        assert "volatility" in risk_metrics
        assert "sharpe_ratio" in risk_metrics or "max_drawdown" in risk_metrics

        print("[✅] 성과 리포트 생성 성공")


class TestLongTermMonitoringScenarios:
    """장기 모니터링 시나리오 테스트"""

    def test_scenario_4_year_monitoring(self, db_session):
        """시나리오 8.1: 4년 후 상담
        
        - 총 투자액: 8,640만원 (월 180만원 × 48개월)
        - 현재 평가액: 약 1억 1,500만원
        - 수익률: +33.1%
        - 연평균 수익률: 약 9.8%
        """
        # 사용자 생성
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="longterm_test@example.com",
            password="testpass123",
            name="김철수",
            age=32,
            occupation="IT 개발자"
        )

        # 투자 성향 설정
        pref_service = InvestmentPreferenceService(db_session)
        preference = pref_service.create_or_update_preference(
            user_id=user.id,
            risk_tolerance=5,
            target_return=8.0,
            investment_period=InvestmentPeriod.MEDIUM,
            investment_experience=InvestmentExperience.BEGINNER,
            max_loss_tolerance=15.0,
            preferred_assets=[AssetType.STOCK, AssetType.ETF]
        )

        # 4년간 투자 시뮬레이션
        investment_service = InvestmentService(db_session)
        
        for month in range(48):
            investment_date = datetime.now() - timedelta(days=30*(48-month))
            
            # 매월 동일한 비율로 투자
            monthly_investments = [
                ("KODEX 국고채3년", AssetType.ETF, Decimal("360000")),
                ("KODEX 미국채권", AssetType.ETF, Decimal("360000")),
                ("KODEX 200", AssetType.ETF, Decimal("450000")),
                ("KODEX 미국S&P500", AssetType.ETF, Decimal("360000")),
                ("KODEX 나스닥100", AssetType.ETF, Decimal("270000"))
            ]
            
            for asset_name, asset_type, amount in monthly_investments:
                # 연평균 9.8% 수익률 시뮬레이션
                years_passed = month / 12
                price_increase = 1 + (0.098 * years_passed)
                current_price = Decimal("10000") * Decimal(str(price_increase))
                
                investment_service.create_investment(
                    user_id=user.id,
                    asset_name=asset_name,
                    asset_type=asset_type,
                    amount=amount,
                    purchase_price=Decimal("10000"),
                    current_price=current_price,
                    purchase_date=investment_date
                )

        # 포트폴리오 분석
        portfolio_service = PortfolioService(db_session)
        portfolio_summary = portfolio_service.get_portfolio_summary(user.id)

        # 검증
        assert portfolio_summary is not None

        # 총 투자액 확인 (8,640만원)
        total_invested = Decimal("86400000")
        assert abs(portfolio_summary["total_invested"] - total_invested) < Decimal("100000")

        # 수익률 확인 (약 33.1%)
        return_rate = portfolio_summary["total_return_rate"]
        assert 30.0 <= return_rate <= 40.0, f"수익률이 예상 범위를 벗어남: {return_rate}%"

        # 연평균 수익률 계산
        years = 4
        annualized_return = ((1 + return_rate/100) ** (1/years) - 1) * 100
        assert 8.0 <= annualized_return <= 11.0, f"연평균 수익률이 예상 범위를 벗어남: {annualized_return}%"

        print(f"[✅] 4년 후 포트폴리오 모니터링 성공")
        print(f"[INFO] 총 투자액: {portfolio_summary['total_invested']:,}원")
        print(f"[INFO] 현재 평가액: {portfolio_summary['total_value']:,}원")
        print(f"[INFO] 수익률: {return_rate:.2f}%")
        print(f"[INFO] 연평균 수익률: {annualized_return:.2f}%")

    def test_scenario_goal_adjustment_recommendation(self, db_session):
        """목표 조정 추천 시나리오 테스트
        
        - 목표 금액: 3억원
        - 현재 자산: 1억 6,500만원
        - 부족 금액: 1억 3,500만원
        - 대안 제시: 목표 조정, 대출 활용, 투자 기간 연장
        """
        # 사용자 생성
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="goal_adjustment@example.com",
            password="testpass123",
            name="김철수",
            age=32,
            occupation="IT 개발자"
        )

        # 재무 목표 설정
        from src.services.financial_goal_service import FinancialGoalService
        goal_service = FinancialGoalService(db_session)
        goal = goal_service.create_goal(
            user_id=user.id,
            goal_type=GoalType.HOUSE,
            target_amount=Decimal("300000000"),  # 3억원
            target_date=datetime.now() + timedelta(days=365),  # 1년 후
            priority=1
        )

        # 현재 자산 시뮬레이션 (1억 6,500만원)
        current_assets = Decimal("165000000")

        # 목표 달성 가능성 분석
        gap_analysis = goal_service.analyze_goal_gap(
            user_id=user.id,
            goal_id=goal.id,
            current_assets=current_assets
        )

        # 검증
        assert gap_analysis is not None
        assert "gap_amount" in gap_analysis
        assert "achievement_probability" in gap_analysis
        assert "recommendations" in gap_analysis

        # 부족 금액 확인
        gap_amount = gap_analysis["gap_amount"]
        expected_gap = Decimal("135000000")  # 1억 3,500만원
        assert abs(gap_amount - expected_gap) < Decimal("1000000")

        # 추천 사항 확인
        recommendations = gap_analysis["recommendations"]
        assert len(recommendations) > 0

        # 추천 유형 확인
        recommendation_types = [r["type"] for r in recommendations]
        expected_types = ["goal_adjustment", "loan_utilization", "period_extension"]
        assert any(t in recommendation_types for t in expected_types)

        print(f"[✅] 목표 조정 추천 생성 성공")
        print(f"[INFO] 부족 금액: {gap_amount:,}원")
        print(f"[INFO] 추천 사항 수: {len(recommendations)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
