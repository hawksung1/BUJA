# 로그인 문제 해결 가이드

## 문제: "Database is not available" 오류

### 원인
데이터베이스가 초기화되지 않아서 발생하는 문제입니다. `asyncpg`가 설치되지 않았거나 PostgreSQL이 실행되지 않았을 수 있습니다.

### 빠른 해결 방법

로그인 페이지에서 **"🔍 진단 정보"**를 클릭하면 자동으로 문제를 진단하고 해결 방법을 제시합니다.

### 수동 해결 방법

#### 1. asyncpg 설치 확인 및 설치
```powershell
# asyncpg 설치 확인
.\.venv\Scripts\python.exe -c "import asyncpg; print('OK')"

# 설치되지 않았다면 설치
# uv 사용 시:
uv pip install asyncpg

# 또는 pip 사용 시:
pip install asyncpg
```

#### 2. .env.local 파일 생성
프로젝트 루트 디렉토리에 `.env.local` 파일을 생성하고 다음 내용을 추가:

```env
# Local Development Environment Variables
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/buja_local
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true
```

#### 3. PostgreSQL 데이터베이스 시작
```powershell
# Docker로 PostgreSQL 시작
docker-compose -f docker-compose.local.yml up -d postgres

# 데이터베이스가 준비될 때까지 대기 (약 10초)
```

#### 4. 데이터베이스 마이그레이션 실행
```powershell
# 마이그레이션 적용
.\.venv\Scripts\python.exe -m alembic upgrade head

# 또는 uv 사용 시:
uv run alembic upgrade head
```

#### 5. Admin 계정 생성 (선택사항)
```powershell
# Admin 계정 생성 스크립트 실행
.\.venv\Scripts\python.exe scripts/create_admin_user.py
```

### 확인 방법

1. **로그인 페이지에서 자동 진단:**
   - 로그인 시도 시 "🔍 진단 정보" 확장 패널에서 자동으로 확인 가능
   - asyncpg 설치 여부, 데이터베이스 URL 등이 표시됨

2. **수동 확인:**
```powershell
# 데이터베이스 연결 확인
.\.venv\Scripts\python.exe -c "from config.database import db; print('Engine:', 'OK' if db.engine else 'NOT INITIALIZED')"

# Admin 계정 확인
.\.venv\Scripts\python.exe -c "import asyncio; from src.repositories import UserRepository; from config.database import db; async def check(): repo = UserRepository(db); user = await repo.get_by_email('admin'); print('Admin user:', 'EXISTS' if user else 'NOT FOUND'); asyncio.run(check())"
```

### 에러 메시지

- **"❌ 데이터베이스 연결 오류"**: 데이터베이스 엔진이 초기화되지 않음
  - 해결: asyncpg 설치, PostgreSQL 시작, .env.local 파일 생성, 마이그레이션 실행
- **"Invalid credentials"**: 사용자가 존재하지 않거나 비밀번호가 틀림
- **"Database connection error"**: PostgreSQL이 실행되지 않음

### 추가 도움말

- `SETUP_DATABASE.md`: 데이터베이스 설정 가이드
- `docs/MIGRATION_GUIDE.md`: 마이그레이션 가이드
- 로그인 페이지의 "🔍 진단 정보" 패널: 실시간 문제 진단

