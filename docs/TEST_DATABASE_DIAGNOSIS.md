# 데이터베이스 진단 기능 테스트 가이드

## 변경 사항 요약

### 1. 로그인 페이지 개선 (`pages/login.py`)
- 데이터베이스 연결 오류 시 자동 진단 기능 추가
- "🔍 진단 정보" 확장 패널로 상세 정보 제공
- asyncpg 설치 여부, 데이터베이스 URL, 해결 방법 표시

### 2. 테스트 케이스 추가 (`tests/e2e/test_streamlit_login.py`)
- `test_database_error_diagnosis`: 데이터베이스 오류 진단 기능 테스트

## 테스트 실행 방법

### 사전 준비

1. **Streamlit 앱 실행** (별도 터미널):
```powershell
# uv 사용 시
& "$env:USERPROFILE\.local\bin\uv.exe" run streamlit run app.py --server.address localhost --server.port 8501

# 또는 가상환경 사용 시
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address localhost --server.port 8501
```

2. **데이터베이스 연결 해제 상태로 테스트** (선택사항):
   - 데이터베이스가 연결되어 있으면 오류 메시지가 표시되지 않을 수 있음
   - 테스트를 위해 PostgreSQL을 중지하거나 `.env.local` 파일을 제거

### 단위 테스트 실행

```powershell
# 단위 테스트만 실행
& "$env:USERPROFILE\.local\bin\uv.exe" run pytest tests/unit/test_auth_middleware.py -v

# 또는
.\.venv\Scripts\python.exe -m pytest tests/unit/test_auth_middleware.py -v
```

### E2E 테스트 실행

```powershell
# 로그인 페이지 테스트 (데이터베이스 진단 포함)
& "$env:USERPROFILE\.local\bin\uv.exe" run pytest tests/e2e/test_streamlit_login.py::TestLoginPage::test_database_error_diagnosis -v -s

# 전체 로그인 페이지 테스트
& "$env:USERPROFILE\.local\bin\uv.exe" run pytest tests/e2e/test_streamlit_login.py -v -s

# 모든 E2E 테스트
& "$env:USERPROFILE\.local\bin\uv.exe" run pytest tests/e2e/ -v -s -m e2e
```

### 수동 UI 테스트

1. 브라우저에서 `http://localhost:8501/login` 접속
2. 이메일과 비밀번호 입력 (예: `test@example.com` / `testpassword`)
3. "Login" 버튼 클릭
4. 데이터베이스가 연결되지 않은 경우:
   - "❌ 데이터베이스 연결 오류" 메시지 확인
   - "🔍 진단 정보" 패널이 자동으로 표시되는지 확인
   - 패널을 클릭하여 확장
   - 다음 정보가 표시되는지 확인:
     - asyncpg 설치 여부
     - 데이터베이스 URL (비밀번호 마스킹됨)
     - 해결 방법 단계별 가이드

## 테스트 시나리오

### 시나리오 1: asyncpg 미설치 상태
1. asyncpg 제거 (테스트용)
2. 로그인 시도
3. 진단 정보에서 "❌ asyncpg가 설치되지 않았습니다" 확인
4. 설치 명령어 확인

### 시나리오 2: PostgreSQL 미실행 상태
1. PostgreSQL 중지
2. 로그인 시도
3. 진단 정보에서 데이터베이스 URL 확인
4. PostgreSQL 시작 방법 확인

### 시나리오 3: .env.local 파일 없음
1. `.env.local` 파일 제거
2. 로그인 시도
3. 진단 정보에서 기본 데이터베이스 URL 확인
4. `.env.local` 파일 생성 방법 확인

### 시나리오 4: 정상 연결 상태
1. 모든 설정 완료 (asyncpg 설치, PostgreSQL 실행, .env.local 설정)
2. 로그인 시도
3. 진단 정보가 표시되지 않고 정상 로그인 진행 확인

## 예상 결과

### 데이터베이스 미연결 시
- ❌ 에러 메시지: "데이터베이스 연결 오류"
- 🔍 진단 정보 패널 자동 표시
- ✅/❌ asyncpg 설치 상태
- 📋 데이터베이스 URL (마스킹됨)
- 📝 해결 방법 4단계

### 데이터베이스 연결 시
- 정상 로그인 진행 또는 자격증명 오류 메시지
- 진단 정보 패널 미표시

## 스크린샷 확인

테스트 실행 후 다음 스크린샷이 생성됩니다:
- `tests/e2e/screenshots/08_database_error_diagnosis.png`: 진단 정보 표시
- `tests/e2e/screenshots/09_diagnosis_expanded.png`: 확장된 진단 정보

## 문제 해결

### 테스트가 실패하는 경우

1. **Streamlit 앱이 실행되지 않음**
   - `ensure_app_running` fixture가 앱을 찾지 못함
   - 별도 터미널에서 Streamlit 앱 실행 확인

2. **Playwright 브라우저 오류**
   - `npx playwright install` 실행 필요

3. **데이터베이스가 연결되어 있어 오류가 표시되지 않음**
   - 정상 동작임
   - 테스트를 위해 PostgreSQL을 중지하거나 잘못된 DATABASE_URL 설정

## 참고 문서

- `docs/LOGIN_TROUBLESHOOTING.md`: 로그인 문제 해결 가이드
- `SETUP_DATABASE.md`: 데이터베이스 설정 가이드
- `docs/PLAYWRIGHT_UI_TEST_GUIDE.md`: Playwright UI 테스트 가이드

