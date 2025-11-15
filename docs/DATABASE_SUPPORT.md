# 데이터베이스 지원 가이드

## 지원하는 데이터베이스

현재 프로젝트는 여러 데이터베이스를 지원하도록 구조화되어 있습니다:

### ✅ 현재 지원

1. **SQLite** (기본값, Docker 불필요)
   - 드라이버: `aiosqlite`
   - URL 형식: `sqlite+aiosqlite:///./data/buja.db`
   - 장점: 별도 서버 설치 불필요, 개발 환경에 적합

2. **PostgreSQL** (선택사항)
   - 드라이버: `asyncpg`
   - URL 형식: `postgresql+asyncpg://user:password@localhost:5432/buja`
   - 장점: 프로덕션 환경에 적합, 고성능

### 🔧 확장 가능한 구조

다른 데이터베이스를 추가하려면:

1. **드라이버 설치**
   ```bash
   # MySQL/MariaDB
   pip install aiomysql
   
   # 기타 데이터베이스
   pip install <driver>
   ```

2. **config/database.py 수정**
   - `is_sqlite`, `is_postgres`와 같은 체크 로직에 새 DB 타입 추가
   - 필요한 드라이버 import 및 검증 추가

3. **config/settings.py 수정**
   - 기본 URL 또는 환경별 URL 설정

## 사용 방법

### SQLite 사용 (기본, 권장)

```env
# .env.local (선택사항, 기본값이 SQLite)
DATABASE_URL=sqlite+aiosqlite:///./data/buja.db
```

설치:
```bash
pip install aiosqlite
```

### PostgreSQL 사용

```env
# .env.local
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/buja_local
```

설치:
```bash
pip install asyncpg
docker-compose -f docker-compose.local.yml up -d postgres
```

## 구조 설계

### 1. Database 클래스 (`config/database.py`)

- **자동 감지**: URL을 분석하여 데이터베이스 타입 자동 감지
- **드라이버 검증**: 필요한 드라이버가 설치되어 있는지 확인
- **유연한 설정**: 각 DB 타입에 맞는 최적 설정 자동 적용

```python
# SQLite: NullPool, 파일 기반
# PostgreSQL: QueuePool, 연결 풀 사용
```

### 2. Settings 클래스 (`config/settings.py`)

- **환경별 기본값**: 개발/테스트/프로덕션 환경별 기본 DB 설정
- **유연한 구성**: 환경 변수로 쉽게 변경 가능

### 3. 마이그레이션 (`migrations/env.py`)

- **다중 DB 지원**: 여러 비동기 드라이버 접두사 자동 처리
- **동기식 변환**: Alembic용 동기식 URL 자동 변환

## 데이터베이스 전환

### SQLite → PostgreSQL

1. `.env.local` 파일 수정:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/buja_local
   ```

2. PostgreSQL 시작:
   ```bash
   docker-compose -f docker-compose.local.yml up -d postgres
   ```

3. 마이그레이션 실행:
   ```bash
   alembic upgrade head
   ```

### PostgreSQL → SQLite

1. `.env.local` 파일 수정:
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./data/buja.db
   ```

2. 마이그레이션 실행:
   ```bash
   alembic upgrade head
   ```

## 새로운 데이터베이스 추가 예시

### MySQL/MariaDB 추가

1. `config/database.py`에 추가:
```python
is_mysql = "mysql" in self.database_url.lower() or "mariadb" in self.database_url.lower()

if is_mysql:
    try:
        import aiomysql
    except ImportError:
        logger.error("aiomysql not installed. Please install: pip install aiomysql")
        # ...
```

2. `migrations/env.py`에 드라이버 접두사 추가:
```python
for prefix in ["+asyncpg", "+aiosqlite", "+aiomysql"]:
    db_url = db_url.replace(prefix, "")
```

3. `pyproject.toml`에 의존성 추가:
```toml
"aiomysql>=0.2.0",  # MySQL async driver
```

## 주의사항

1. **마이그레이션**: 데이터베이스를 전환할 때는 마이그레이션을 다시 실행해야 합니다.
2. **데이터 마이그레이션**: 기존 데이터가 있다면 별도로 마이그레이션해야 합니다.
3. **기능 차이**: 일부 SQL 기능은 데이터베이스마다 다를 수 있습니다.

## 권장 사항

- **개발 환경**: SQLite (간단, 빠른 설정)
- **테스트 환경**: SQLite (속도, 격리)
- **프로덕션 환경**: PostgreSQL (성능, 안정성)

