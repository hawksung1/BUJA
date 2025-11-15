# E2E 테스트 가이드

## 개요

이 디렉토리에는 Streamlit 앱의 End-to-End (E2E) 테스트가 포함되어 있습니다.

## 테스트 파일

### 1. `test_streamlit_app.py`
- 기본 HTTP 기반 E2E 테스트
- 앱이 실행 중인지 확인
- 페이지 로드 및 기본 요소 확인

### 2. `test_streamlit_playwright.py`
- Playwright를 사용한 브라우저 테스트 준비
- Playwright MCP 통합을 위한 구조 제공

### 3. `test_playwright_mcp.py`
- Playwright MCP를 직접 사용하는 테스트
- 실제 브라우저에서 화면 테스트 수행

## 실행 방법

### 사전 준비

1. **Streamlit 앱 실행**
   ```bash
   cd /mnt/f/git_projects/BUJA
   uv run streamlit run app.py
   ```

2. **의존성 설치**
   ```bash
   uv sync
   ```

### 테스트 실행

#### 모든 E2E 테스트 실행
```bash
pytest tests/e2e/ -v -m e2e
```

#### Playwright MCP 테스트만 실행
```bash
pytest tests/e2e/ -v -m playwright
```

#### 특정 테스트 파일 실행
```bash
pytest tests/e2e/test_streamlit_app.py -v
```

#### 느린 테스트 제외
```bash
pytest tests/e2e/ -v -m "e2e and not slow"
```

## Playwright MCP 사용

### 설정

Playwright MCP 서버가 설정되어 있어야 합니다. `.cursor/mcp-servers.json` 또는 MCP 설정 파일에서 확인하세요.

### 테스트 작성 가이드

Playwright MCP를 사용한 테스트는 다음과 같은 패턴을 따릅니다:

```python
@pytest.mark.playwright
def test_example():
    # 1. 브라우저로 URL 이동
    # mcp_playwright_browser_navigate(url="http://localhost:8501")
    
    # 2. 페이지 스냅샷 확인
    # snapshot = mcp_playwright_browser_snapshot()
    
    # 3. 요소 클릭
    # mcp_playwright_browser_click(element="버튼", ref="...")
    
    # 4. 텍스트 입력
    # mcp_playwright_browser_type(element="입력 필드", ref="...", text="텍스트")
    
    # 5. 스크린샷 촬영
    # mcp_playwright_browser_take_screenshot(filename="screenshot.png")
```

### 사용 가능한 Playwright MCP 도구

- `mcp_playwright_browser_navigate`: URL로 이동
- `mcp_playwright_browser_snapshot`: 페이지 스냅샷 가져오기
- `mcp_playwright_browser_click`: 요소 클릭
- `mcp_playwright_browser_type`: 텍스트 입력
- `mcp_playwright_browser_fill_form`: 폼 필드 입력
- `mcp_playwright_browser_take_screenshot`: 스크린샷 촬영
- `mcp_playwright_browser_evaluate`: JavaScript 실행
- 기타 Playwright MCP 도구들

## 테스트 마커

- `@pytest.mark.e2e`: E2E 테스트
- `@pytest.mark.slow`: 느린 테스트 (실제 브라우저 사용)
- `@pytest.mark.playwright`: Playwright MCP를 사용하는 테스트

## 주의사항

1. **앱 실행 필요**: E2E 테스트는 Streamlit 앱이 실행 중이어야 합니다.
2. **시간 소요**: 실제 브라우저를 사용하는 테스트는 시간이 걸릴 수 있습니다.
3. **환경 의존성**: Playwright MCP 서버가 설정되어 있어야 합니다.
4. **포트 충돌**: 다른 프로세스가 8501 포트를 사용하지 않는지 확인하세요.

## 문제 해결

### 앱이 실행되지 않음
```bash
# 포트 확인
netstat -ano | grep 8501

# 앱 재시작
uv run streamlit run app.py
```

### Playwright MCP 연결 실패
- MCP 서버 설정 확인
- Playwright MCP 서버 재시작

### 테스트 실패
- 앱이 정상적으로 실행 중인지 확인
- 브라우저 콘솔 오류 확인
- 스크린샷 확인 (자동 저장됨)

