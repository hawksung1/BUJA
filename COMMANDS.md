# BUJA 프로젝트 명령어 가이드

## 개발 서버 실행
```bash
# Streamlit 앱 실행
uv run streamlit run app.py

# 포트 지정
uv run streamlit run app.py --server.port 8501
```

## 의존성 관리
```bash
# 의존성 설치/동기화
uv sync

# 패키지 추가
uv add package-name

# 개발 의존성 추가
uv add --dev package-name
```

## 테스트
```bash
# 전체 테스트
uv run pytest

# 단위 테스트
uv run pytest tests/unit/ -v

# 통합 테스트
uv run pytest tests/integration/ -v

# E2E 테스트
uv run pytest tests/e2e/ -v -m e2e

# 커버리지 포함
uv run pytest --cov=src --cov-report=html --cov-report=term-missing
```

## 코드 품질
```bash
# 린트
uv run ruff check .

# 포맷
uv run black .

# 타입 체크
uv run mypy src
```

## 데이터베이스 관리
```bash
# SQLite 데이터베이스 초기화
uv run python scripts/init_sqlite_db.py

# PostgreSQL (Docker)
docker-compose -f docker-compose.local.yml up -d postgres
docker-compose -f docker-compose.local.yml down
docker-compose -f docker-compose.local.yml logs -f postgres

# 관리자 계정 생성
uv run python scripts/create_admin_user.py
```
