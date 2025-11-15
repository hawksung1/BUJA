# SQLite 로그인 오류 수정 가이드

## 문제
현재 `.env.local` 파일에 PostgreSQL 설정이 있어서 SQLite로 전환해야 합니다.

## 해결 방법

### 방법 1: .env.local 파일 수정 (권장)

`.env.local` 파일을 열어서 다음 부분을 수정하세요:

**변경 전:**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/buja_local
```

**변경 후:**
```env
DATABASE_URL=sqlite+aiosqlite:///./data/buja.db
```

### 방법 2: .env.local 파일 삭제

`.env.local` 파일을 삭제하면 기본값(SQLite)이 사용됩니다.

## 다음 단계

1. **마이그레이션 실행:**
   ```bash
   alembic upgrade head
   ```

2. **Streamlit 앱 재시작**

3. **로그인 테스트**

## 확인 사항

- ✅ aiosqlite 설치 완료
- ✅ 기본값이 SQLite로 설정됨
- ⏳ .env.local 파일 수정 필요
- ⏳ 마이그레이션 실행 필요

