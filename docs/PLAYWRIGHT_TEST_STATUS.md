# Playwright E2E 테스트 현황

## 문제점

1. **Streamlit 앱이 시작되지 않음**
   - `.venv`에 `streamlit`이 설치되지 않음
   - `uv sync`로 의존성 설치 필요

2. **데이터베이스 연결 필요**
   - PostgreSQL이 실행 중이어야 함
   - `docker-compose.local.yml`로 데이터베이스 시작 필요

3. **테스트가 스킵됨**
   - `ensure_app_running` fixture가 Streamlit 앱을 찾지 못함
   - Streamlit이 실제로 실행되지 않아서 발생

## 해결 방법

### 1. 의존성 설치
```powershell
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
& "$env:USERPROFILE\.local\bin\uv.exe" run --no-project python -m pytest tests/e2e/test_streamlit_full_flow.py::test_login_with_admin_credentials -v -s --no-cov
```

## 테스트 파일

- `tests/e2e/test_streamlit_full_flow.py`: 전체 로그인/회원가입 플로우 테스트
  - `test_login_with_admin_credentials`: Admin 계정으로 로그인 테스트
  - `TestFullLoginFlow::test_complete_login_flow`: 완전한 로그인 플로우
  - `TestFullRegisterFlow::test_complete_register_flow`: 완전한 회원가입 플로우

## 테스트 내용

각 테스트는 다음을 수행합니다:
1. 브라우저 열기 (`headless=False`로 실제 브라우저 표시)
2. Streamlit 앱 접속
3. 로그인 페이지로 이동
4. 이메일/비밀번호 입력
5. 로그인 버튼 클릭
6. 응답 확인 (성공 메시지 또는 페이지 전환)
7. 스크린샷 저장 (`tests/e2e/screenshots/`)

## 다음 단계

1. 의존성 설치 완료 확인
2. 데이터베이스 실행 확인
3. Streamlit 앱 정상 실행 확인
4. Playwright 테스트 실행 및 결과 확인

