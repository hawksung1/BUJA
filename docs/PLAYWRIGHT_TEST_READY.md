# Playwright E2E 테스트 준비 완료

## ✅ 완료된 작업

### 1. 테스트 코드 작성
- `tests/e2e/test_streamlit_full_flow.py`: 전체 플로우 테스트
  - ✅ `test_login_with_admin_credentials`: Admin 계정 로그인 테스트
  - ✅ `TestFullLoginFlow::test_complete_login_flow`: 완전한 로그인 플로우
  - ✅ `TestFullRegisterFlow::test_complete_register_flow`: 완전한 회원가입 플로우

### 2. 테스트 내용
각 테스트는 다음을 수행합니다:
1. ✅ 브라우저 열기 (`headless=False` - 실제 브라우저 표시)
2. ✅ Streamlit 앱 접속 (`http://localhost:8501`)
3. ✅ 로그인 페이지로 이동 (메인 페이지에서 자동 리다이렉트)
4. ✅ 이메일 입력 필드 찾기 및 입력
5. ✅ 비밀번호 입력 필드 찾기 및 입력
6. ✅ 로그인 버튼 클릭
7. ✅ 응답 확인 (성공 메시지 또는 페이지 전환)
8. ✅ 스크린샷 저장 (`tests/e2e/screenshots/`)

### 3. Fixture 설정
- ✅ `browser`: Playwright 브라우저 인스턴스 (`headless=False`, `slow_mo=500`)
- ✅ `page`: 각 테스트마다 새로운 페이지
- ✅ `ensure_app_running`: Streamlit 앱 실행 확인 (스킵하지 않고 경고만 출력)
- ✅ `screenshot_dir`: 스크린샷 저장 디렉토리

## ⚠️ 현재 문제점

### 1. 의존성 설치 실패
```
error: command 'cmake' failed: None
hint: pyarrow (v21.0.0) requires cmake for building
```

**해결 방법:**
- Windows에서 C++ 빌드 도구 설치 필요
- 또는 `pyarrow`를 제외하고 다른 방법 사용

### 2. Streamlit 미설치
- `.venv`에 `streamlit`이 설치되지 않음
- `uv sync` 실행 필요 (하지만 `pyarrow` 빌드 실패로 차단됨)

### 3. 데이터베이스 미실행
- Docker가 설치되지 않았거나 PATH에 없음
- PostgreSQL이 실행 중이어야 함

## 🎯 테스트 실행 방법 (환경 설정 후)

### 1. 의존성 설치
```powershell
# C++ 빌드 도구 설치 후
cd F:\git_projects\BUJA
& "$env:USERPROFILE\.local\bin\uv.exe" sync
```

### 2. 데이터베이스 시작
```powershell
docker-compose -f docker-compose.local.yml up -d
```

### 3. Streamlit 앱 시작
```powershell
& "$env:USERPROFILE\.local\bin\uv.exe" run streamlit run app.py --server.address localhost --server.port 8501
```

### 4. Playwright 테스트 실행
```powershell
# 단일 테스트
& "$env:USERPROFILE\.local\bin\uv.exe" run --no-project python -m pytest tests/e2e/test_streamlit_full_flow.py::test_login_with_admin_credentials -v -s --no-cov

# 전체 테스트
& "$env:USERPROFILE\.local\bin\uv.exe" run --no-project python -m pytest tests/e2e/test_streamlit_full_flow.py -v -s --no-cov
```

## 📝 테스트 코드 구조

```python
@pytest.mark.e2e
@pytest.mark.playwright
def test_login_with_admin_credentials(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """admin 계정으로 실제 로그인 테스트"""
    # 1. 메인 페이지로 이동
    page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
    
    # 2. 이메일 입력
    email_input = page.locator("input[type='text']").first
    email_input.fill("admin")
    
    # 3. 비밀번호 입력
    password_input = page.locator("input[type='password']").first
    password_input.fill("admin")
    
    # 4. 로그인 버튼 클릭
    submit_button = page.locator("button[type='submit']").first
    submit_button.click()
    
    # 5. 응답 확인
    body_text = page.locator("body").inner_text()
    # 성공 여부 확인
```

## ✅ 다음 단계

1. **환경 설정 완료**
   - C++ 빌드 도구 설치
   - `uv sync` 실행
   - Docker 설치 및 실행

2. **테스트 실행**
   - Streamlit 앱 시작
   - Playwright 테스트 실행
   - 스크린샷 확인

3. **결과 확인**
   - `tests/e2e/screenshots/` 디렉토리에서 스크린샷 확인
   - 테스트 로그에서 각 단계 확인

## 📸 예상 스크린샷

테스트 실행 후 다음 스크린샷이 생성됩니다:
- `admin_login_form.png`: 로그인 폼 입력 전
- `admin_login_result.png`: 로그인 제출 후
- `01_login_page.png`: 로그인 페이지 로드
- `02_login_form_filled.png`: 폼 입력 완료
- `03_after_login_click.png`: 로그인 버튼 클릭 후

