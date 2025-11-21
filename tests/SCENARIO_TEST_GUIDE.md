# 시나리오 기반 테스트 가이드

이 문서는 `USER_SCENARIO.md`에 정의된 사용자 시나리오를 기반으로 작성된 테스트 코드에 대한 설명입니다.

## 📋 테스트 구조

### 1. E2E 테스트 (End-to-End Tests)

#### `test_onboarding_scenario.py`
**시나리오 2단계: 온보딩 프로세스**

- ✅ Step 1: 기본 정보 입력
- ✅ Step 2: 재무 상황 입력
- ✅ Step 3: 투자 성향 설정
- ✅ Step 4: 재무 목표 설정

**실행 방법:**
```bash
uv run pytest tests/e2e/test_onboarding_scenario.py -v
```

#### `test_scenario_korean_response.py`
**시나리오 4단계: Agent Chat - 첫 상담**

- ✅ 한국어 질문에 한국어로 응답
- ✅ 기본 정보 재요청 없음
- ✅ 포트폴리오 분석 요청 (시나리오 4.7)
- ✅ 증권사 추천 및 수수료 정보 요청 (시나리오 4.9)
- ✅ 공격적 투자 전략 요청 (시나리오 4.5)
- ✅ 채팅 히스토리 저장 및 로드

**실행 방법:**
```bash
uv run pytest tests/e2e/test_scenario_korean_response.py -v
```

**테스트 함수:**
- `test_korean_response_in_chat`: 한국어 응답 확인
- `test_chat_history_persistence`: 채팅 히스토리 저장
- `test_portfolio_analysis_request`: 포트폴리오 분석 요청
- `test_brokerage_recommendation_request`: 증권사 추천 요청
- `test_aggressive_strategy_request`: 공격적 전략 요청

#### `test_user_scenario.py`
**전체 사용자 시나리오 통합 테스트**

- ✅ 로그인
- ✅ 온보딩 (스킵 가능)
- ✅ Agent Chat 접속
- ✅ 첫 번째 질문 (주택 구매 목표)
- ✅ 두 번째 질문 (포트폴리오 분석)
- ✅ 세 번째 질문 (공격적 전략)
- ✅ 네 번째 질문 (증권사 정보)
- ✅ 채팅 히스토리 확인
- ✅ Dashboard 확인

**실행 방법:**
```bash
uv run pytest tests/e2e/test_user_scenario.py -v
```

### 2. 통합 테스트 (Integration Tests)

#### `test_portfolio_monitoring_scenarios.py`
**시나리오 6-8단계: 포트폴리오 모니터링 및 장기 관리**

**TestPortfolioMonitoringScenarios 클래스:**
- ✅ `test_scenario_1_month_monitoring`: 1개월 후 상담 (시나리오 6.1)
  - 총 투자액: 180만원
  - 수익률: +1.1%
  - 자산별 성과 확인

- ✅ `test_scenario_6_month_monitoring`: 6개월 후 상담 (시나리오 7.1)
  - 총 투자액: 1,080만원
  - 수익률: +6.5%
  - 연환산 수익률: 약 13%
  - 리스크 분석

- ✅ `test_scenario_rebalancing_recommendation`: 리밸런싱 추천
  - 포트폴리오 비중 확인
  - 리밸런싱 필요 여부 판단
  - 리밸런싱 계획 생성

- ✅ `test_scenario_goal_progress_tracking`: 재무 목표 진행률 추적
  - 목표 진행률 계산
  - 목표 달성 예상 시뮬레이션

- ✅ `test_scenario_performance_report`: 성과 리포트 생성
  - 월별/연별 성과 리포트
  - 주요 지표: 수익률, 리스크, 샤프 비율

**TestLongTermMonitoringScenarios 클래스:**
- ✅ `test_scenario_4_year_monitoring`: 4년 후 상담 (시나리오 8.1)
  - 총 투자액: 8,640만원
  - 현재 평가액: 약 1억 1,500만원
  - 수익률: +33.1%
  - 연평균 수익률: 약 9.8%

- ✅ `test_scenario_goal_adjustment_recommendation`: 목표 조정 추천
  - 목표 금액: 3억원
  - 현재 자산: 1억 6,500만원
  - 부족 금액: 1억 3,500만원
  - 대안 제시: 목표 조정, 대출 활용, 투자 기간 연장

**실행 방법:**
```bash
uv run pytest tests/integration/test_portfolio_monitoring_scenarios.py -v
```

#### `test_global_portfolio_scenarios.py`
**글로벌 포트폴리오 시나리오**

- ✅ 한국 거주 투자자, 글로벌 분산 투자
- ✅ 공격적 투자자, 헷지 없음
- ✅ 보수적 투자자, 전체 헷지
- ✅ 다중 지역 통화 분산
- ✅ 신흥 시장 집중 투자

**실행 방법:**
```bash
uv run pytest tests/integration/test_global_portfolio_scenarios.py -v
```

## 🚀 전체 시나리오 테스트 실행

### 모든 시나리오 테스트 실행
```bash
# E2E 테스트
uv run pytest tests/e2e/test_onboarding_scenario.py tests/e2e/test_scenario_korean_response.py tests/e2e/test_user_scenario.py -v

# 통합 테스트
uv run pytest tests/integration/test_portfolio_monitoring_scenarios.py tests/integration/test_global_portfolio_scenarios.py -v

# 전체 테스트
uv run pytest tests/e2e/test_*scenario*.py tests/integration/test_*scenario*.py -v
```

### 특정 시나리오만 실행
```bash
# 온보딩 시나리오만
uv run pytest tests/e2e/test_onboarding_scenario.py::test_onboarding_complete_flow -v

# 1개월 모니터링 시나리오만
uv run pytest tests/integration/test_portfolio_monitoring_scenarios.py::TestPortfolioMonitoringScenarios::test_scenario_1_month_monitoring -v

# 4년 후 모니터링 시나리오만
uv run pytest tests/integration/test_portfolio_monitoring_scenarios.py::TestLongTermMonitoringScenarios::test_scenario_4_year_monitoring -v
```

## 📊 시나리오 커버리지

| 시나리오 단계 | 테스트 파일 | 상태 |
|-------------|-----------|------|
| 1. 회원가입 및 로그인 | `test_onboarding_scenario.py` | ✅ |
| 2. 온보딩 프로세스 | `test_onboarding_scenario.py` | ✅ |
| 3. 대시보드 확인 | `test_user_scenario.py` | ✅ |
| 4. Agent Chat - 첫 상담 | `test_scenario_korean_response.py`, `test_user_scenario.py` | ✅ |
| 5. 투자 실행 및 포트폴리오 등록 | `test_portfolio_monitoring_scenarios.py` | ✅ |
| 6. 정기 상담 (1개월 후) | `test_portfolio_monitoring_scenarios.py` | ✅ |
| 7. 장기 모니터링 (6개월 후) | `test_portfolio_monitoring_scenarios.py` | ✅ |
| 8. 목표 달성 전 최종 점검 (4년 후) | `test_portfolio_monitoring_scenarios.py` | ✅ |

## 🔍 주요 검증 항목

### E2E 테스트
- ✅ 한국어 응답 확인
- ✅ 기본 정보 재요청 없음
- ✅ 포트폴리오 관련 키워드 포함
- ✅ 증권사/수수료 정보 제공
- ✅ 전략 관련 내용 포함
- ✅ 채팅 히스토리 저장 및 로드
- ✅ Dashboard 요소 확인

### 통합 테스트
- ✅ 포트폴리오 평가액 계산
- ✅ 수익률 계산 (1개월, 6개월, 4년)
- ✅ 리스크 지표 계산 (변동성, 최대 낙폭)
- ✅ 리밸런싱 필요 여부 판단
- ✅ 재무 목표 진행률 추적
- ✅ 목표 달성 예상 시뮬레이션
- ✅ 성과 리포트 생성
- ✅ 목표 조정 추천

## 📝 테스트 실행 시 주의사항

### E2E 테스트
1. **Streamlit 앱 실행 필요**: E2E 테스트는 실제 앱이 실행 중이어야 합니다.
   ```bash
   uv run streamlit run app.py
   ```

2. **로그인 정보**: 일부 테스트는 기존 사용자 계정이 필요할 수 있습니다.
   - 기본 계정: `admin@example.com` / `admin123`

3. **API 키 설정**: LLM 응답 테스트는 OpenAI API 키가 필요합니다.
   - 사이드바에서 API 키 설정

4. **스크린샷**: 테스트 실행 중 스크린샷이 `tests/e2e/screenshots/` 디렉토리에 저장됩니다.

### 통합 테스트
1. **데이터베이스**: 테스트용 데이터베이스가 자동으로 생성됩니다.
2. **Fixture**: `db_session` fixture가 자동으로 제공됩니다.
3. **격리**: 각 테스트는 독립적으로 실행되며 서로 영향을 주지 않습니다.

## 🐛 트러블슈팅

### E2E 테스트 실패 시
1. Streamlit 앱이 실행 중인지 확인
2. 브라우저 드라이버가 설치되어 있는지 확인
3. 스크린샷을 확인하여 UI 상태 파악

### 통합 테스트 실패 시
1. 데이터베이스 연결 확인
2. 서비스 로직 검증
3. 테스트 데이터 확인

## 📚 참고 문서
- [USER_SCENARIO.md](../../docs/USER_SCENARIO.md): 전체 사용자 시나리오
- [pytest 문서](https://docs.pytest.org/)
- [Playwright 문서](https://playwright.dev/python/)
