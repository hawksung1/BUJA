# Playwright UI 테스트 가이드

## 브라우저가 보이도록 설정

테스트 파일 `tests/e2e/test_playwright_python.py`에서 **`headless=False`**로 설정되어 있습니다:

```python
browser = playwright.chromium.launch(headless=False, slow_mo=500)
```

이렇게 하면 브라우저 창이 실제로 열립니다.

## WSL 환경에서 브라우저 보기

WSL 환경에서는 GUI가 없어서 브라우저 창이 보이지 않을 수 있습니다. 다음 방법을 사용하세요:

### 방법 1: 스크린샷 확인

브라우저가 열리지 않아도 스크린샷으로 확인할 수 있습니다:

```bash
# WSL에서
cd /mnt/f/git_projects/BUJA
~/.local/bin/uv run python -m pytest tests/e2e/test_playwright_python.py::TestStreamlitWithPlaywright::test_page_screenshot -v --no-cov -s

# 스크린샷 확인
ls -lh tests/e2e/screenshots/
```

### 방법 2: X11 Forwarding (Windows)

Windows에서 X11 서버를 설치하고 브라우저를 볼 수 있습니다:

1. **VcXsrv** 또는 **X410** 설치
2. WSL에서 DISPLAY 설정:
   ```bash
   export DISPLAY=:0
   ```

### 방법 3: 테스트 스크립트 사용

자동으로 Streamlit을 실행하고 테스트하는 스크립트:

```bash
# WSL에서
cd /mnt/f/git_projects/BUJA
bash tests/e2e/run_ui_test.sh
```

## 테스트 실행

### 1. Streamlit 앱 실행

```bash
# WSL에서
cd /mnt/f/git_projects/BUJA
~/.local/bin/uv run streamlit run app.py --server.address localhost --server.port 8501
```

### 2. 테스트 실행 (브라우저 보기)

```bash
# WSL에서 (별도 터미널)
cd /mnt/f/git_projects/BUJA
~/.local/bin/uv run python -m pytest tests/e2e/test_playwright_python.py -v --no-cov -s
```

**`-s` 옵션**: 출력을 보기 위해 사용

## 확인 방법

### 스크린샷으로 확인

테스트가 실행되면 `tests/e2e/screenshots/` 디렉토리에 스크린샷이 저장됩니다:

```bash
# WSL에서
ls -lh tests/e2e/screenshots/
```

### 브라우저 창 확인

- Windows에서 X11 서버가 실행 중이면 브라우저 창이 보입니다
- WSL에서 직접 실행하면 브라우저는 백그라운드에서 실행되지만 스크린샷으로 확인 가능

## 현재 설정

- ✅ `headless=False`: 브라우저가 보이도록 설정
- ✅ `slow_mo=500`: 동작을 천천히 실행 (관찰하기 쉽게)
- ✅ 스크린샷 자동 저장

## 문제 해결

### 브라우저가 보이지 않는 경우

1. **스크린샷 확인**: `tests/e2e/screenshots/` 디렉토리 확인
2. **X11 서버 설치**: Windows에서 VcXsrv 설치
3. **DISPLAY 설정**: `export DISPLAY=:0`

### Streamlit 연결 실패

```bash
# Streamlit 앱이 실행 중인지 확인
curl http://localhost:8501

# 실행 중이 아니면 시작
~/.local/bin/uv run streamlit run app.py --server.address localhost --server.port 8501
```

