# UI 테스트 가이드

## 개요

BUJA 프로젝트의 UI 테스트는 **기능 테스트와 UI 연동 테스트를 명확히 구분**하여 구성되어 있습니다.

## 테스트 구조

### 1. 기능 테스트 (Unit/Integration Tests)

**위치**: `tests/unit/`, `tests/integration/`

**목적**: 백엔드 로직 검증
- 서비스 로직 (NotificationService, PortfolioMonitoringService 등)
- Repository 로직
- 모델 검증
- 비즈니스 로직 검증

**예시**:
- `tests/unit/test_notification_service.py` - NotificationService 로직 검증
- `tests/unit/test_portfolio_monitoring_service.py` - PortfolioMonitoringService 로직 검증
- `tests/unit/test_goal_tracking_service.py` - GoalTrackingService 로직 검증

### 2. UI 연동 테스트 (E2E Browser Tests)

**위치**: `tests/e2e/`

**목적**: 실제 브라우저에서 UI 동작 검증
- UI 요소 렌더링 확인
- 사용자 상호작용 검증
- 페이지 네비게이션 검증
- 실제 사용자 경험 검증

**구분**:
- **UI Integration Tests** (`test_ui_integration.py`): UI 요소가 제대로 렌더링되고 상호작용이 올바르게 동작하는지 검증
- **UI Functionality Tests** (`test_ui_functionality.py`): 브라우저에서 UI를 통해 실제 기능이 동작하는지 검증
- **UI Feature Tests**: 특정 기능의 UI 테스트

## UI 테스트 파일 구조

### 알림 시스템 UI 테스트

**파일**: `tests/e2e/test_ui_notification.py`

**테스트 항목**:
- 알림 페이지 UI 요소 검증
- 사이드바 알림 배지 UI 검증
- 알림 페이지 네비게이션 검증
- 알림 필터 기능 검증

**실행**:
```bash
uv run pytest tests/e2e/test_ui_notification.py -v -m ui
```

### 포트폴리오 모니터링 UI 테스트

**파일**: `tests/e2e/test_ui_portfolio_monitoring.py`

**테스트 항목**:
- 포트폴리오 모니터링 대시보드 표시 검증
- 포트폴리오 모니터링 알림 표시 검증
- 포트폴리오 모니터링 채팅 통합 검증

**실행**:
```bash
uv run pytest tests/e2e/test_ui_portfolio_monitoring.py -v -m ui
```

### 목표 추적 UI 테스트

**파일**: `tests/e2e/test_ui_goal_tracking.py`

**테스트 항목**:
- 목표 추적 대시보드 표시 검증
- 목표 추적 알림 표시 검증
- 목표 추적 채팅 통합 검증

**실행**:
```bash
uv run pytest tests/e2e/test_ui_goal_tracking.py -v -m ui
```

### 자율적 Agent UI 통합 테스트

**파일**: `tests/e2e/test_ui_autonomous_agent.py`

**테스트 항목**:
- 자율적 Agent 알림 표시 검증
- 자율적 Agent 채팅 통합 검증
- 자율적 Agent 대시보드 통합 검증

**실행**:
```bash
uv run pytest tests/e2e/test_ui_autonomous_agent.py -v -m ui
```

## 테스트 실행 방법

### 사전 준비

1. **Streamlit 앱 실행**
   ```bash
   cd f:\git_projects\BUJA
   uv run streamlit run app.py
   ```

2. **의존성 확인**
   ```bash
   uv sync
   ```

### 모든 UI 테스트 실행

```bash
uv run pytest tests/e2e/ -v -m ui
```

### 특정 UI 테스트 실행

```bash
# 알림 시스템 UI 테스트만
uv run pytest tests/e2e/test_ui_notification.py -v

# 포트폴리오 모니터링 UI 테스트만
uv run pytest tests/e2e/test_ui_portfolio_monitoring.py -v

# 목표 추적 UI 테스트만
uv run pytest tests/e2e/test_ui_goal_tracking.py -v

# 자율적 Agent UI 테스트만
uv run pytest tests/e2e/test_ui_autonomous_agent.py -v
```

### UI 테스트만 실행 (기능 테스트 제외)

```bash
uv run pytest tests/e2e/ -v -m "ui and not unit"
```

### 스크린샷 확인

UI 테스트 실행 시 스크린샷이 `tests/e2e/screenshots/` 디렉토리에 저장됩니다.

## 테스트 작성 가이드

### UI 테스트 작성 패턴

```python
"""
기능 테스트와 구분:
- 기능 테스트: 백엔드 로직만 검증 (서비스, 모델, 레포지토리)
- UI 테스트: 실제 브라우저에서 UI가 제대로 렌더링되고 상호작용이 올바르게 동작하는지 검증
"""
import time
import pytest
from playwright.sync_api import Page
from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load

@pytest.mark.e2e
@pytest.mark.ui
class TestFeatureUI:
    """기능 UI 테스트 클래스"""

    def test_feature_ui_elements(
        self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str
    ):
        """기능 UI 요소 검증"""
        # 로그인
        # 페이지 이동
        # UI 요소 확인
        # 스크린샷 저장
        pass
```

### 주요 Fixture

- `page`: Playwright Page 인스턴스
- `app_url`: Streamlit 앱 URL (기본: http://localhost:8501)
- `ensure_app_running`: 앱이 실행 중인지 확인
- `screenshot_dir`: 스크린샷 저장 디렉토리

### 헬퍼 함수

- `wait_for_streamlit_load(page)`: Streamlit 페이지 로드 대기
- `take_screenshot(page, filename, screenshot_dir)`: 스크린샷 저장

## 주의사항

1. **앱 실행 필요**: UI 테스트는 Streamlit 앱이 실행 중이어야 합니다.
2. **비동기 처리**: Streamlit은 비동기로 렌더링되므로 적절한 대기 시간이 필요합니다.
3. **알림 없음**: 일부 테스트는 알림이 없을 수도 있으므로, 알림이 없어도 정상으로 처리합니다.
4. **스크린샷**: 테스트 실패 시 스크린샷을 확인하여 문제를 진단할 수 있습니다.

## CI/CD 통합

UI 테스트는 CI/CD 파이프라인에서 실행할 수 있도록 구성되어 있습니다.

```yaml
# 예시: GitHub Actions
- name: Run UI tests
  run: |
    uv run streamlit run app.py &
    sleep 10
    uv run pytest tests/e2e/ -v -m ui
```

## 관련 문서

- [E2E 테스트 가이드](./tests/e2e/README.md)
- [알림 시스템 설계](./NOTIFICATION_DESIGN.md)
- [자율적 Agent 구현 요약](./AUTONOMOUS_AGENT_IMPLEMENTATION_SUMMARY.md)

