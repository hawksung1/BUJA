# UI 테스트 가이드

## 테스트 분류

### 1. 기능 테스트 (Unit/Integration Tests)
**위치**: `tests/unit/`, `tests/integration/`

- 백엔드 로직 검증
- 서비스, 모델, 레포지토리 테스트
- 비즈니스 로직 검증
- 데이터베이스 연동 테스트

**예시**:
- `test_notification_service.py` - 알림 서비스 로직 테스트
- `test_portfolio_monitoring_service.py` - 포트폴리오 모니터링 로직 테스트
- `test_goal_tracking_service.py` - 목표 추적 로직 테스트

### 2. UI 연동 테스트 (UI Integration Tests)
**위치**: `tests/e2e/test_ui_integration.py`

- 실제 브라우저에서 UI 요소 렌더링 검증
- UI 요소 존재 및 가시성 확인
- 사용자 인터페이스 레이아웃 검증
- 반응형 디자인 검증

**테스트 항목**:
- 로그인 페이지 UI 요소
- 대시보드 UI 렌더링
- Agent Chat UI 상호작용
- 사이드바 네비게이션 UI
- 온보딩 UI 플로우
- 프로필 페이지 UI
- 투자 선호도 페이지 UI
- 반응형 UI 레이아웃

### 3. UI 기능 테스트 (UI Functionality Tests)
**위치**: `tests/e2e/test_ui_functionality.py`

- 실제 브라우저에서 사용자 액션을 통한 기능 검증
- 클릭, 입력, 제출 등의 상호작용 테스트
- 실제 기능 동작 확인

**테스트 항목**:
- 로그인 기능
- 채팅 메시지 전송 기능
- 포트폴리오 표시 기능
- 페이지 네비게이션 기능
- 폼 제출 기능
- 에러 처리 UI
- 데이터 지속성 UI

## 테스트 실행

### 사전 준비

1. **Streamlit 앱 실행**
   ```bash
   uv run streamlit run app.py --server.address localhost --server.port 8501
   ```

2. **Playwright 브라우저 설치** (최초 1회)
   ```bash
   uv run playwright install chromium
   ```

### 테스트 실행

#### UI 연동 테스트만 실행
```bash
uv run pytest tests/e2e/test_ui_integration.py -v -m ui
```

#### UI 기능 테스트만 실행
```bash
uv run pytest tests/e2e/test_ui_functionality.py -v -m ui_functionality
```

#### 모든 UI 테스트 실행
```bash
uv run pytest tests/e2e/test_ui_integration.py tests/e2e/test_ui_functionality.py -v
```

#### 특정 테스트만 실행
```bash
uv run pytest tests/e2e/test_ui_integration.py::TestUIIntegration::test_login_page_ui_elements -v
```

#### 브라우저 보이기 (headless=False)
기본적으로 `conftest.py`에서 `headless=False`로 설정되어 있습니다.

#### 스크린샷 확인
테스트 실행 후 `tests/e2e/screenshots/` 디렉토리에서 스크린샷을 확인할 수 있습니다.

## 테스트 구조

### UI 연동 테스트 (`test_ui_integration.py`)

```python
class TestUIIntegration:
    """UI 연동 테스트 클래스"""
    
    def test_login_page_ui_elements(self, ...):
        """로그인 페이지 UI 요소 검증"""
        # UI 요소 존재 확인
        # 가시성 확인
        # 입력 가능 여부 확인
```

### UI 기능 테스트 (`test_ui_functionality.py`)

```python
class TestUIFunctionality:
    """UI 기능 테스트 클래스"""
    
    def test_login_functionality(self, ...):
        """로그인 기능 검증"""
        # 실제 로그인 시도
        # 성공/실패 확인
        # 결과 검증
```

## 테스트 마커

- `@pytest.mark.e2e`: E2E 테스트 마커
- `@pytest.mark.ui`: UI 연동 테스트 마커
- `@pytest.mark.ui_functionality`: UI 기능 테스트 마커

## 주의사항

1. **Streamlit 앱이 실행 중이어야 함**
   - 테스트 실행 전에 `uv run streamlit run app.py` 실행 필요

2. **테스트 데이터**
   - 일부 테스트는 기존 사용자 데이터를 사용합니다
   - 테스트용 사용자 생성이 필요할 수 있습니다

3. **타이밍 이슈**
   - Streamlit은 비동기적으로 렌더링되므로 `wait_for_streamlit_load()` 사용
   - 필요시 `time.sleep()` 추가

4. **스크린샷**
   - 모든 테스트에서 스크린샷을 자동으로 저장합니다
   - `tests/e2e/screenshots/` 디렉토리 확인

## 문제 해결

### 브라우저가 열리지 않는 경우

1. Playwright 브라우저 설치 확인:
   ```bash
   uv run playwright install chromium
   ```

2. `conftest.py`에서 `headless=False` 확인

### Streamlit 연결 실패

1. Streamlit 앱이 실행 중인지 확인:
   ```bash
   curl http://localhost:8501
   ```

2. 포트 번호 확인 (기본: 8501)

### 테스트 실패

1. 스크린샷 확인: `tests/e2e/screenshots/`
2. 로그 확인: 테스트 출력 메시지
3. Streamlit 콘솔 로그 확인

