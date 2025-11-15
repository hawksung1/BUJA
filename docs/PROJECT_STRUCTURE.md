# 프로젝트 구조

BUJA 프로젝트의 폴더 구조와 각 디렉토리의 역할을 설명합니다.

## 디렉토리 구조

```
BUJA/
├── app.py                 # Streamlit 메인 애플리케이션 진입점
├── pyproject.toml         # 프로젝트 설정 및 의존성 관리
├── pytest.ini            # pytest 설정
├── alembic.ini            # Alembic 마이그레이션 설정
│
├── config/                # 설정 파일
│   ├── __init__.py
│   ├── settings.py        # 애플리케이션 설정
│   ├── database.py        # 데이터베이스 연결 설정
│   └── logging.py         # 로깅 설정
│
├── pages/                 # Streamlit 페이지 파일
│   ├── login.py          # 로그인 페이지
│   ├── register.py       # 회원가입 페이지
│   ├── dashboard.py      # 대시보드 페이지
│   ├── agent_chat.py     # 에이전트 채팅 페이지
│   ├── profile.py        # 프로필 페이지
│   ├── onboarding.py     # 온보딩 페이지
│   ├── investment_preference.py  # 투자 선호도 페이지
│   └── mcp_tools.py      # MCP 도구 페이지
│
├── src/                   # 소스 코드
│   ├── agents/            # AI 에이전트
│   │   ├── base_agent.py
│   │   ├── investment_agent.py
│   │   └── tools/         # 에이전트 도구
│   │
│   ├── analyzers/         # 분석기
│   │   ├── portfolio_analyzer.py
│   │   ├── risk_analyzer.py
│   │   ├── performance_analyzer.py
│   │   └── asset_allocator.py
│   │
│   ├── models/            # 데이터 모델
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── chat.py
│   │   ├── chat_project.py
│   │   ├── investment.py
│   │   ├── portfolio.py
│   │   └── financial.py
│   │
│   ├── repositories/     # 데이터 접근 계층
│   │   ├── base_repository.py
│   │   ├── user_repository.py
│   │   ├── chat_repository.py
│   │   ├── chat_project_repository.py
│   │   ├── investment_repository.py
│   │   └── portfolio_repository.py
│   │
│   ├── services/         # 비즈니스 로직
│   │   ├── user_service.py
│   │   ├── chat_service.py
│   │   ├── chat_project_service.py
│   │   ├── investment_service.py
│   │   ├── portfolio_service.py
│   │   ├── recommendation_service.py
│   │   ├── investment_preference_service.py
│   │   ├── currency_hedge_service.py
│   │   ├── mcp_tool_service.py
│   │   └── screenshot_service.py
│   │
│   ├── middleware/        # 미들웨어
│   │   ├── auth_middleware.py
│   │   └── error_handler.py
│   │
│   ├── external/          # 외부 서비스 클라이언트
│   │   └── llm_client.py
│   │
│   ├── utils/             # 유틸리티 함수
│   │   ├── security.py
│   │   ├── validators.py
│   │   ├── formatters.py
│   │   ├── converters.py
│   │   ├── async_helpers.py
│   │   └── sidebar.py
│   │
│   └── exceptions.py      # 커스텀 예외
│
├── tests/                 # 테스트 코드
│   ├── unit/              # 단위 테스트
│   ├── integration/       # 통합 테스트
│   └── e2e/               # E2E 테스트
│       ├── screenshots/   # 테스트 스크린샷
│       └── conftest.py    # pytest 설정
│
├── scripts/               # 유틸리티 스크립트
│   ├── create_admin_user.py
│   ├── init_sqlite_db.py
│   ├── setup_local_db.ps1
│   ├── setup_local_db.sh
│   ├── setup_git_hooks.ps1
│   ├── setup_git_hooks.sh
│   ├── validate_setup.py
│   ├── start_streamlit.ps1
│   ├── start_streamlit.bat
│   ├── run_playwright_test.ps1
│   └── run_playwright_test_ui.ps1
│
├── migrations/            # 데이터베이스 마이그레이션
│   ├── env.py
│   └── script.py.mako
│
├── data/                  # 데이터 파일
│   ├── buja.db           # SQLite 데이터베이스
│   └── mcp_tools/        # MCP 도구 데이터
│
└── docs/                  # 문서
    ├── README.md         # 문서 인덱스
    ├── REQUIREMENTS.md   # 요구사항
    ├── DESIGN.md         # 설계 문서
    ├── WBS.md            # 작업 분해 구조
    ├── USER_SCENARIO.md  # 사용자 시나리오
    ├── TEST_COVERAGE.md  # 테스트 커버리지
    └── ...               # 기타 문서들
```

## 주요 디렉토리 설명

### `config/`
애플리케이션 설정 파일들이 위치합니다.
- `settings.py`: 환경 변수 및 애플리케이션 설정
- `database.py`: 데이터베이스 연결 및 세션 관리
- `logging.py`: 로깅 설정

### `pages/`
Streamlit 페이지 파일들입니다. 각 파일은 독립적인 페이지로 동작합니다.

### `src/`
핵심 비즈니스 로직이 위치합니다.
- **agents/**: AI 에이전트 구현
- **analyzers/**: 포트폴리오 분석 로직
- **models/**: SQLAlchemy 데이터 모델
- **repositories/**: 데이터 접근 계층 (DAO 패턴)
- **services/**: 비즈니스 로직 계층
- **middleware/**: 인증 및 에러 처리 미들웨어
- **external/**: 외부 API 클라이언트
- **utils/**: 공통 유틸리티 함수

### `tests/`
테스트 코드가 위치합니다.
- **unit/**: 단위 테스트
- **integration/**: 통합 테스트
- **e2e/**: End-to-End 테스트 (Playwright 사용)

### `scripts/`
유틸리티 스크립트들이 위치합니다.
- 데이터베이스 초기화
- 관리자 사용자 생성
- Git hooks 설정
- 테스트 실행 스크립트

### `docs/`
프로젝트 문서들이 위치합니다.

## 파일 명명 규칙

- **Python 파일**: `snake_case.py`
- **테스트 파일**: `test_*.py`
- **스크립트 파일**: `snake_case.py` 또는 `kebab-case.ps1`
- **문서 파일**: `UPPER_SNAKE_CASE.md`

## 참고

- 프로젝트 구조 변경 시 이 문서를 업데이트해주세요.
- 새로운 모듈 추가 시 적절한 디렉토리에 배치하세요.


