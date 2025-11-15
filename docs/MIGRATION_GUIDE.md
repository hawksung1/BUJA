# 데이터베이스 마이그레이션 가이드

## 초기 마이그레이션 생성

### 1. 데이터베이스 생성

PostgreSQL 데이터베이스를 생성합니다:

```bash
# PostgreSQL 접속
psql -U postgres

# 데이터베이스 생성
CREATE DATABASE buja;

# 사용자 생성 (선택사항)
CREATE USER buja_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE buja TO buja_user;
```

### 2. 환경 변수 설정

`.env` 파일에 데이터베이스 URL을 설정합니다:

```env
DATABASE_URL=postgresql+asyncpg://buja_user:your_password@localhost:5432/buja
```

### 3. 초기 마이그레이션 생성

```bash
# Alembic으로 초기 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 생성된 마이그레이션 파일 검토
# migrations/versions/xxxx_initial_migration.py 파일 확인
```

### 4. 마이그레이션 적용

```bash
# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 상태 확인
alembic current
alembic history
```

### 5. 마이그레이션 롤백 (필요시)

```bash
# 이전 버전으로 롤백
alembic downgrade -1

# 특정 리비전으로 롤백
alembic downgrade <revision_id>
```

## 새로운 마이그레이션 생성

모델을 변경한 후:

```bash
# 자동 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 수동 마이그레이션 생성
alembic revision -m "설명"
```

## 마이그레이션 파일 구조

```python
"""Initial migration

Revision ID: xxxx
Revises: 
Create Date: 2024-01-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxxx'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 테이블 생성
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        # ...
    )
    # ...

def downgrade() -> None:
    # 테이블 삭제
    op.drop_table('users')
    # ...
```

## 주의사항

1. **마이그레이션 파일 검토**: 자동 생성된 마이그레이션은 항상 검토하세요
2. **데이터 백업**: 프로덕션 환경에서는 마이그레이션 전 백업 필수
3. **테스트 환경에서 먼저 테스트**: 프로덕션 적용 전 테스트 환경에서 검증

---

**문서 버전**: 1.0




