# 알림 테이블 마이그레이션 가이드

## 마이그레이션 생성

다음 명령어로 마이그레이션 파일을 생성하세요:

```bash
# uv 사용 시
uv run alembic revision --autogenerate -m "Add notification table"

# 또는 python 직접 사용
python -m alembic revision --autogenerate -m "Add notification table"
```

## 수동 마이그레이션 파일 생성

만약 자동 생성이 안 되면, `migrations/versions/` 디렉토리에 다음 내용으로 파일을 생성하세요:

```python
"""Add notification table

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2024-xx-xx
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = 'xxxxx'
down_revision = 'yyyyy'  # 이전 마이그레이션 ID
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')
```

## 마이그레이션 실행

```bash
uv run alembic upgrade head
```

