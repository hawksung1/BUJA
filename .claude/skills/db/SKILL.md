---
name: db
description: BUJA PostgreSQL 데이터베이스 작업을 수행한다. 마이그레이션 생성/실행, 스키마 확인, Docker PostgreSQL 컨테이너 관리를 담당한다.
---

# DB Skill

## 사용법

```
/db [migrate|status|reset|new <name>]
```

## 서브커맨드

### `/db status`
현재 마이그레이션 상태 확인
```bash
docker compose up -d db
uv run alembic current
uv run alembic history
```

### `/db new <name>`
새 마이그레이션 파일 생성
```bash
uv run alembic revision --autogenerate -m "<name>"
```

### `/db migrate`
모든 미적용 마이그레이션 실행
```bash
uv run alembic upgrade head
```

### `/db reset`
DB 초기화 (개발 환경 전용 — 사용자 확인 필요)
```bash
uv run alembic downgrade base
uv run alembic upgrade head
```

## 주의사항

- `reset`은 반드시 사용자 확인 후 실행
- 프로덕션 환경에서 `reset` 금지
- 마이그레이션 전 QA 에이전트의 안전성 검증 권장
