# UI 테스트 실행 가이드

## ⚠️ 중요: 브라우저가 열립니다!

UI 테스트는 **실제 브라우저 창이 열립니다**. 화면을 확인할 수 있습니다!

## 사전 준비

### 1. Streamlit 앱 실행 (필수!)

**별도 터미널에서 먼저 실행해야 합니다:**

```bash
cd f:\git_projects\BUJA
uv run streamlit run app.py
```

앱이 `http://localhost:8501`에서 실행되는지 확인하세요.

### 2. 브라우저 확인

테스트 실행 시:
- ✅ **브라우저 창이 자동으로 열립니다**
- ✅ **화면을 직접 확인할 수 있습니다**
- ✅ **각 단계가 천천히 실행됩니다** (slow_mo=1500ms)

## 테스트 실행

### 단일 테스트 실행

```bash
# 알림 페이지 UI 테스트
uv run pytest tests/e2e/test_ui_notification.py::TestNotificationUI::test_notification_page_ui_elements -v -s --no-cov

# 포트폴리오 모니터링 UI 테스트
uv run pytest tests/e2e/test_ui_portfolio_monitoring.py -v -s --no-cov

# 목표 추적 UI 테스트
uv run pytest tests/e2e/test_ui_goal_tracking.py -v -s --no-cov

# 자율적 Agent UI 테스트
uv run pytest tests/e2e/test_ui_autonomous_agent.py -v -s --no-cov
```

### 모든 UI 테스트 실행

```bash
uv run pytest tests/e2e/ -v -m ui -s --no-cov
```

## 테스트 실행 과정

1. **브라우저 시작**
   ```
   [BROWSER] 브라우저를 시작합니다...
   [WARNING] 브라우저 창이 열립니다. 화면을 확인하세요!
   [OK] 브라우저가 열렸습니다!
   ```

2. **페이지 열기**
   ```
   [PAGE] 새 페이지가 열렸습니다: about:blank
   ```

3. **테스트 실행**
   - 각 단계가 천천히 실행됩니다 (1.5초 간격)
   - 브라우저에서 실제 동작을 확인할 수 있습니다
   - 스크린샷이 `tests/e2e/screenshots/`에 저장됩니다

4. **브라우저 종료**
   ```
   [CLOSE] 브라우저를 닫습니다...
   ```

## 문제 해결

### 브라우저가 안 열리는 경우

1. **Playwright 브라우저 설치 확인**
   ```bash
   uv run playwright install chromium
   ```

2. **브라우저 프로세스 확인**
   - 작업 관리자에서 Chrome/Chromium 프로세스 확인
   - 다른 브라우저가 실행 중이면 종료 후 재시도

### Streamlit 연결 실패

```
[WARN] Streamlit 앱이 http://localhost:8501에서 응답하지 않습니다
```

**해결 방법:**
1. Streamlit 앱이 실행 중인지 확인
2. 포트 8501이 사용 중인지 확인
3. 다른 터미널에서 앱을 실행했는지 확인

### 스크린샷 확인

테스트 실행 후 `tests/e2e/screenshots/` 디렉토리에서 스크린샷을 확인할 수 있습니다.

## 테스트 옵션

### 브라우저를 더 천천히 실행

`conftest.py`에서 `slow_mo` 값을 조정:
```python
slow_mo=2000,  # 2초 간격
```

### 브라우저를 백그라운드로 실행 (headless)

`conftest.py`에서:
```python
headless=True,  # 브라우저 창이 안 보임
```

## 참고

- 브라우저는 **세션 전체에서 공유**됩니다 (모든 테스트가 같은 브라우저 사용)
- 각 테스트마다 **새 페이지**가 열립니다
- 테스트 실패 시에도 **스크린샷이 저장**됩니다

