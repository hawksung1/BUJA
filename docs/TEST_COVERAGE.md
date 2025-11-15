# 테스트 커버리지 문서

## 개요
BUJA 프로젝트의 테스트 커버리지 및 테스트 파일 목록입니다.

## 단위 테스트 (Unit Tests)

### 모델 테스트
- **test_models.py**: 모든 데이터베이스 모델 테스트
  - User, UserProfile
  - FinancialSituation, FinancialGoal
  - InvestmentPreference, InvestmentRecord
  - Screenshot, PortfolioAnalysis, AssetRecommendation, RebalancingHistory

### Repository 테스트
- **test_repositories.py**: Repository 패턴 테스트
  - BaseRepository
  - UserRepository
  - InvestmentRecordRepository
  - PortfolioAnalysisRepository

### Service 테스트
- **test_user_service.py**: UserService 테스트
  - 회원가입, 로그인
  - 프로필 업데이트
  - 재무 상황 업데이트
  - 투자 성향 업데이트

- **test_investment_preference_service.py**: InvestmentPreferenceService 테스트
  - 설문조사 기반 위험 감수 성향 계산
  - 투자 성향 분석 리포트 생성

- **test_recommendation_service.py**: RecommendationService 테스트
  - 최초 자산 구성 추천 생성

- **test_investment_service.py**: InvestmentService 테스트
  - 투자 기록 CRUD
  - 투자 기록 통계

- **test_portfolio_service.py**: PortfolioService 테스트
  - 포트폴리오 분석
  - 자산 배분 조회

- **test_screenshot_service.py**: ScreenshotService 테스트
  - 이미지 검증
  - 스크린샷 업로드

### Analyzer 테스트
- **test_analyzers.py**: 분석기 테스트
  - AssetAllocator
  - PortfolioAnalyzer
  - PerformanceAnalyzer
  - RiskAnalyzer

### External 테스트
- **test_llm_client.py**: LLM 클라이언트 테스트
  - RateLimiter
  - OpenAIProvider
  - AnthropicProvider
  - LLMClient

### Agent 테스트
- **test_agents.py**: Agent 테스트
  - BaseAgent
  - InvestmentAgent
  - ConversationMessage

### Middleware 테스트
- **test_auth_middleware.py**: AuthMiddleware 테스트
  - 인증 확인
  - 로그인/로그아웃
  - 세션 관리

## 통합 테스트 (Integration Tests)
- 현재 미구현 (향후 추가 예정)

## E2E 테스트 (End-to-End Tests)
- 현재 미구현 (향후 Playwright로 구현 예정)

## 테스트 실행 방법

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/unit/test_user_service.py

# 커버리지 포함 실행
pytest --cov=src --cov-report=html
```

## 커버리지 목표
- 단위 테스트: 80% 이상
- 통합 테스트: 60% 이상
- E2E 테스트: 주요 시나리오 커버

