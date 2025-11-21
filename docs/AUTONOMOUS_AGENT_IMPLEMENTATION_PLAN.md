# 자율적 Agent 구현 계획

> 자산 구매/판매 및 학습 기능 제외, 모니터링/알림/계획 수립 중심

## 📋 목표

BUJA의 InvestmentAgent를 **완전 자율 Agent**로 전환:
- ✅ 백그라운드 모니터링
- ✅ 자동 알림 시스템
- ✅ 목표 추적 및 진행률 모니터링
- ✅ 능동적 조언 제공 (구매/판매 제외)
- ✅ 장기 계획 수립

## 🏗️ 아키텍처 개요

```
┌─────────────────────────────────────────┐
│  Streamlit App (app.py)                 │
│  └─ 사용자 인터페이스                    │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Background Scheduler Service           │
│  └─ 주기적 모니터링 실행                 │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Portfolio Monitoring Service            │
│  ├─ 포트폴리오 분석                      │
│  ├─ 리스크 체크                          │
│  ├─ 목표 진행률 체크                     │
│  └─ 리밸런싱 필요성 체크                 │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Autonomous Investment Agent            │
│  ├─ 상황 분석                            │
│  ├─ 액션 플랜 수립                       │
│  └─ 자동 조언 생성                       │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Chat Service                           │
│  └─ 알림 메시지 저장                     │
└─────────────────────────────────────────┘
```

## 📁 파일 구조

```
src/
├── services/
│   ├── portfolio_monitoring_service.py    # [신규] 포트폴리오 모니터링
│   ├── scheduler_service.py                # [신규] 백그라운드 스케줄러
│   ├── notification_service.py             # [신규] 알림 관리
│   └── goal_tracking_service.py            # [신규] 목표 추적
├── agents/
│   └── autonomous_investment_agent.py     # [신규] 자율적 Agent 확장
└── models/
    └── notification.py                     # [신규] 알림 모델

scripts/
└── start_background_worker.py              # [신규] 백그라운드 워커 시작 스크립트
```

## 🎯 구현 단계

### Phase 1: 모니터링 서비스 (1주)

#### 1.1 알림 모델 생성
**파일**: `src/models/notification.py`

```python
"""
알림 모델
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class NotificationType(str, Enum):
    """알림 유형"""
    RISK_ALERT = "risk_alert"              # 리스크 경고
    GOAL_PROGRESS = "goal_progress"        # 목표 진행률
    REBALANCING_NEEDED = "rebalancing"     # 리밸런싱 필요
    PORTFOLIO_REVIEW = "portfolio_review"  # 포트폴리오 리뷰
    GOAL_AT_RISK = "goal_at_risk"         # 목표 달성 위험
    GOAL_NEAR_COMPLETION = "goal_near"     # 목표 달성 임박


class NotificationStatus(str, Enum):
    """알림 상태"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class Notification(Base, TimestampMixin):
    """알림 모델"""
    
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus),
        default=NotificationStatus.UNREAD,
        nullable=False
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 메타데이터 (JSON 형태로 저장)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    
    # 관계
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"
```

**작업**:
- [ ] `src/models/notification.py` 생성
- [ ] `src/models/user.py`에 relationship 추가
- [ ] Alembic 마이그레이션 생성
- [ ] 단위 테스트 작성

#### 1.2 알림 서비스 생성
**파일**: `src/services/notification_service.py`

```python
"""
알림 서비스
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from config.database import db
from config.logging import get_logger
from src.models.notification import Notification, NotificationType, NotificationStatus
from src.repositories.base_repository import BaseRepository

logger = get_logger(__name__)


class NotificationRepository(BaseRepository[Notification]):
    """알림 Repository"""
    pass


class NotificationService:
    """알림 서비스"""
    
    def __init__(self):
        self.repo = NotificationRepository(db)
    
    async def create_notification(
        self,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """알림 생성"""
        import json
        
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            status=NotificationStatus.UNREAD,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        return await self.repo.create(notification)
    
    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """사용자 알림 조회"""
        # TODO: Repository에 쿼리 메서드 추가
        pass
    
    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """알림 읽음 처리"""
        # TODO: 구현
        pass
```

**작업**:
- [ ] `src/services/notification_service.py` 생성
- [ ] Repository 메서드 구현
- [ ] 단위 테스트 작성

#### 1.3 포트폴리오 모니터링 서비스
**파일**: `src/services/portfolio_monitoring_service.py`

**주요 기능**:
1. 포트폴리오 분석
2. 리스크 임계값 체크
3. 목표 진행률 체크
4. 리밸런싱 필요성 체크
5. Agent 액션 트리거

**작업**:
- [ ] 기본 모니터링 로직 구현
- [ ] 리스크 체크 로직 구현
- [ ] 목표 진행률 체크 로직 구현
- [ ] 리밸런싱 체크 로직 구현
- [ ] Agent 연동 구현
- [ ] 단위 테스트 작성

### Phase 2: 목표 추적 서비스 (3일)

#### 2.1 목표 추적 서비스
**파일**: `src/services/goal_tracking_service.py`

**주요 기능**:
1. 목표 진행률 계산
2. 목표 달성 예측
3. 목표 달성 위험도 평가
4. 목표별 추천 생성

**작업**:
- [ ] 목표 진행률 계산 로직
- [ ] 목표 달성 예측 알고리즘
- [ ] 위험도 평가 로직
- [ ] 단위 테스트 작성

### Phase 3: 자율적 Agent 확장 (1주)

#### 3.1 자율적 Agent 구현
**파일**: `src/agents/autonomous_investment_agent.py`

**주요 기능**:
1. 상황 분석 및 액션 플랜 수립
2. 장기 계획 생성
3. 능동적 조언 생성 (구매/판매 제외)
4. 알림 메시지 생성

**작업**:
- [ ] `AutonomousInvestmentAgent` 클래스 구현
- [ ] 액션 플랜 수립 로직
- [ ] 장기 계획 생성 로직
- [ ] 조언 생성 로직
- [ ] 단위 테스트 작성

### Phase 4: 스케줄러 서비스 (3일)

#### 4.1 스케줄러 서비스
**파일**: `src/services/scheduler_service.py`

**주요 기능**:
1. 일일 모니터링 (매일 오전 9시)
2. 주간 리뷰 (매주 월요일)
3. 월간 목표 체크 (매월 1일)
4. 백그라운드 실행

**작업**:
- [ ] 스케줄러 기본 구조 구현
- [ ] 일일/주간/월간 태스크 구현
- [ ] 에러 핸들링 및 재시도 로직
- [ ] 단위 테스트 작성

### Phase 5: 백그라운드 워커 통합 (2일)

#### 5.1 백그라운드 워커 스크립트
**파일**: `scripts/start_background_worker.py`

**작업**:
- [ ] 독립 실행 가능한 워커 스크립트 생성
- [ ] Streamlit과 분리된 프로세스로 실행
- [ ] 로깅 및 모니터링 설정

#### 5.2 Streamlit 통합
**파일**: `app.py`, `pages/agent_chat.py`

**작업**:
- [ ] 알림 표시 UI 추가
- [ ] 알림 읽음 처리 기능
- [ ] 모니터링 상태 표시 (선택)

### Phase 6: 테스트 및 문서화 (3일)

#### 6.1 통합 테스트
**작업**:
- [ ] 모니터링 시나리오 테스트
- [ ] 알림 생성/조회 테스트
- [ ] 스케줄러 실행 테스트
- [ ] E2E 테스트 작성

#### 6.2 문서화
**작업**:
- [ ] API 문서 업데이트
- [ ] 사용자 가이드 작성
- [ ] 아키텍처 문서 업데이트

## 📊 상세 구현 계획

### 1. Portfolio Monitoring Service

```python
# src/services/portfolio_monitoring_service.py

class PortfolioMonitoringService:
    """포트폴리오 자동 모니터링 서비스"""
    
    async def monitor_user_portfolio(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 포트폴리오 모니터링
        
        Returns:
            {
                "risk_alerts": [...],
                "goal_alerts": [...],
                "rebalancing_needed": bool,
                "actions_taken": [...]
            }
        """
        # 1. 포트폴리오 분석
        # 2. 리스크 체크
        # 3. 목표 진행률 체크
        # 4. 리밸런싱 체크
        # 5. 필요한 경우 Agent 액션 트리거
        pass
    
    async def _check_risk_thresholds(
        self, 
        user_id: int, 
        portfolio_analysis: Dict
    ) -> List[Dict[str, Any]]:
        """리스크 임계값 체크"""
        alerts = []
        
        # 최대 낙폭 체크
        # 변동성 체크
        # Sharpe Ratio 체크
        
        return alerts
    
    async def _check_goal_progress(
        self,
        user_id: int,
        goals: List,
        portfolio_value: float
    ) -> List[Dict[str, Any]]:
        """목표 진행률 체크"""
        alerts = []
        
        for goal in goals:
            progress = portfolio_value / goal.target_amount
            days_remaining = (goal.target_date - today).days
            
            # 목표 달성 임박 (90% 이상)
            if progress >= 0.9:
                alerts.append({
                    "type": "goal_near_completion",
                    "goal_id": goal.id,
                    "progress": progress
                })
            
            # 목표 달성 위험 (진행률이 예상보다 낮음)
            expected_progress = 1 - (days_remaining / total_days)
            if progress < expected_progress * 0.8:
                alerts.append({
                    "type": "goal_at_risk",
                    "goal_id": goal.id,
                    "progress": progress,
                    "expected": expected_progress
                })
        
        return alerts
    
    async def _check_rebalancing(
        self,
        user_id: int,
        portfolio_analysis: Dict
    ) -> bool:
        """리밸런싱 필요성 체크"""
        # 목표 자산 배분과 현재 배분 비교
        # 5% 이상 차이 시 리밸런싱 필요
        pass
    
    async def _trigger_agent_action(
        self,
        user_id: int,
        alerts: Dict[str, Any]
    ):
        """Agent가 자동으로 조치 취하기"""
        from src.agents.autonomous_investment_agent import AutonomousInvestmentAgent
        
        agent = AutonomousInvestmentAgent()
        context = {"user_id": user_id}
        
        # 상황에 맞는 메시지 생성
        action_message = self._build_action_message(alerts)
        
        # Agent가 조언 생성
        response = ""
        async for chunk in agent.chat(action_message, context=context):
            response += chunk
        
        # 알림으로 저장
        await self.notification_service.create_notification(
            user_id=user_id,
            type=NotificationType.PORTFOLIO_REVIEW,
            title="포트폴리오 모니터링 결과",
            message=response,
            metadata={"alerts": alerts}
        )
```

### 2. Goal Tracking Service

```python
# src/services/goal_tracking_service.py

class GoalTrackingService:
    """목표 추적 서비스"""
    
    async def calculate_goal_progress(
        self,
        user_id: int,
        goal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """목표 진행률 계산"""
        # 현재 포트폴리오 가치
        # 목표 금액
        # 목표일까지 남은 기간
        # 필요한 월 투자액 계산
        pass
    
    async def predict_goal_achievement(
        self,
        user_id: int,
        goal_id: int
    ) -> Dict[str, Any]:
        """목표 달성 예측"""
        # 현재 진행률
        # 예상 수익률
        # 월 투자액
        # 목표 달성 가능성 계산
        pass
    
    async def assess_goal_risk(
        self,
        user_id: int,
        goal_id: int
    ) -> Dict[str, Any]:
        """목표 달성 위험도 평가"""
        # 진행률 vs 예상 진행률
        # 시간 대비 진행률
        # 리스크 점수 계산
        pass
```

### 3. Autonomous Investment Agent

```python
# src/agents/autonomous_investment_agent.py

class AutonomousInvestmentAgent(InvestmentAgent):
    """자율적 투자 Agent"""
    
    async def create_action_plan(
        self,
        user_id: int,
        situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        상황 분석 및 액션 플랜 수립
        
        Returns:
            {
                "immediate_actions": [...],  # 즉시 조치
                "short_term_plan": [...],   # 단기 계획 (1-3개월)
                "medium_term_plan": [...],   # 중기 계획 (3-6개월)
                "long_term_plan": [...]      # 장기 계획 (6개월+)
            }
        """
        # LLM에게 장기 계획 수립 요청
        planning_prompt = f"""
        다음 상황을 분석하여 구체적인 액션 플랜을 수립해주세요:
        
        {situation}
        
        다음을 포함해주세요:
        1. 즉시 조치가 필요한 사항
        2. 단기 계획 (1-3개월)
        3. 중기 계획 (3-6개월)
        4. 장기 계획 (6개월 이상)
        
        각 액션은 구체적이고 실행 가능해야 합니다.
        """
        
        # Agent 응답 생성
        plan_response = ""
        async for chunk in self.chat(planning_prompt, context={"user_id": user_id}):
            plan_response += chunk
        
        # 구조화된 플랜으로 파싱 (JSON 응답 요청)
        return self._parse_action_plan(plan_response)
    
    async def generate_proactive_advice(
        self,
        user_id: int,
        alert_type: str,
        alert_data: Dict[str, Any]
    ) -> str:
        """능동적 조언 생성"""
        context = {"user_id": user_id}
        
        advice_prompt = f"""
        다음 상황에 대해 사용자에게 조언을 제공해주세요:
        
        알림 유형: {alert_type}
        상황: {alert_data}
        
        구체적이고 실행 가능한 조언을 제공해주세요.
        """
        
        response = ""
        async for chunk in self.chat(advice_prompt, context=context):
            response += chunk
        
        return response
```

### 4. Scheduler Service

```python
# src/services/scheduler_service.py

class SchedulerService:
    """백그라운드 작업 스케줄러"""
    
    async def start(self):
        """스케줄러 시작"""
        await asyncio.gather(
            self._daily_monitoring_loop(),
            self._weekly_review_loop(),
            self._monthly_goal_check_loop()
        )
    
    async def _daily_monitoring_loop(self):
        """매일 포트폴리오 모니터링"""
        while self.running:
            # 매일 오전 9시 실행
            await self._wait_until_time(9, 0)
            await self.monitoring_service.monitor_all_users()
    
    async def _weekly_review_loop(self):
        """주간 리뷰"""
        while self.running:
            # 매주 월요일 오전 10시
            await asyncio.sleep(7 * 24 * 3600)
            if datetime.now().weekday() == 0:
                await self._generate_weekly_review()
    
    async def _monthly_goal_check_loop(self):
        """월간 목표 체크"""
        while self.running:
            # 매월 1일
            await asyncio.sleep(30 * 24 * 3600)
            if datetime.now().day == 1:
                await self._generate_monthly_goal_report()
```

## 🧪 테스트 계획

### 단위 테스트
- [ ] `PortfolioMonitoringService` 테스트
- [ ] `GoalTrackingService` 테스트
- [ ] `NotificationService` 테스트
- [ ] `AutonomousInvestmentAgent` 테스트
- [ ] `SchedulerService` 테스트

### 통합 테스트
- [ ] 모니터링 → 알림 생성 플로우
- [ ] 목표 추적 → Agent 조언 생성 플로우
- [ ] 스케줄러 → 모니터링 실행 플로우

### E2E 테스트
- [ ] 사용자 포트폴리오 모니터링 시나리오
- [ ] 목표 달성 알림 시나리오
- [ ] 리밸런싱 권고 시나리오

## 📅 일정 요약

| Phase | 작업 | 기간 | 우선순위 |
|-------|------|------|----------|
| 1 | 모니터링 서비스 | 1주 | 높음 |
| 2 | 목표 추적 서비스 | 3일 | 높음 |
| 3 | 자율적 Agent | 1주 | 높음 |
| 4 | 스케줄러 서비스 | 3일 | 중간 |
| 5 | 백그라운드 워커 통합 | 2일 | 중간 |
| 6 | 테스트 및 문서화 | 3일 | 높음 |
| **총계** | | **약 3주** | |

## 🚀 실행 순서

1. **Phase 1**: 모니터링 기반 구축
2. **Phase 2**: 목표 추적 기능 추가
3. **Phase 3**: Agent 자율성 확장
4. **Phase 4**: 백그라운드 실행 환경 구축
5. **Phase 5**: 통합 및 UI 연동
6. **Phase 6**: 테스트 및 안정화

## ⚠️ 주의사항

1. **자산 구매/판매 제외**: 모든 조언은 참고용이며, 실제 거래는 사용자가 직접 수행
2. **에러 핸들링**: 백그라운드 작업 실패 시에도 메인 앱에 영향 없도록 설계
3. **성능**: 대량 사용자 모니터링 시 성능 고려 (배치 처리, 비동기)
4. **알림 빈도**: 사용자 경험을 위해 알림 빈도 조절 필요

## 📝 다음 단계

구현 시작 전:
1. [ ] 데이터베이스 마이그레이션 계획 검토
2. [ ] 기존 서비스와의 통합 포인트 확인
3. [ ] 테스트 데이터 준비
4. [ ] 개발 환경 설정

