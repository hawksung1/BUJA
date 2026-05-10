# BUJA — AI 자산관리 어드바이저

워런 버핏 · 벤저민 그레이엄 · 피터 린치 · 레이 달리오 · 필립 피셔의 투자 철학을 기반으로 포트폴리오를 분석하고 리밸런싱을 제안하는 AI 자산관리 서비스입니다.

## 주요 기능

| 기능 | 설명 |
|------|------|
| **포트폴리오 분석** | 보유 종목 전체를 5대 투자자 관점으로 진단, 자산군 배분 평가 |
| **리밸런싱 제안** | 달리오 올웨더 기준 목표 배분 비교, 구체적 매수·매도 액션 제시 |
| **종목 분석** | 가치·성장·매크로·경영 질 종합 판정 + 분할 매수 계획 |
| **거시경제 브리핑** | 경제 4계절 진단, 포트폴리오 영향 및 방어 전략 |
| **환율 리스크** | 해외 자산 분석 시 원/달러 영향·헤지 여부 필수 포함 |
| **뉴스·유튜브** | 네이버 금융 RSS, 머니머니코믹스 최신 인사이트 |

## 5대 투자자 철학

| 투자자 | 핵심 관점 |
|--------|-----------|
| 워런 버핏 | 경제적 해자, ROE 15%+, FCF 기반 내재가치, 장기 보유 |
| 벤저민 그레이엄 | 안전마진 33%+, P/E·P/B 기준값, Mr. Market 활용 |
| 피터 린치 | PEG 1.0 이하, 6분류 체계, 10-bagger 발굴, 현장 조사 |
| 레이 달리오 | 올웨더 배분, 경제 4계절, 부채사이클, 리스크 패리티 |
| 필립 피셔 | 15포인트 체크리스트, Scuttlebutt, 경영진 역량, 성장 질 |

## 빠른 시작

```bash
# 1. 패키지 설치
uv sync

# 2. 환경변수 설정
cp .env.example .env
# .env에 ANTHROPIC_API_KEY 입력

# 3. 앱 실행
uv run streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속 후 왼쪽 사이드바에 보유 종목을 입력하면 바로 분석이 시작됩니다.

## 환경변수

```bash
# 필수
ANTHROPIC_API_KEY=sk-ant-...

# 선택 (NH나무 계좌 자동 조회)
NH_APP_KEY=...
NH_APP_SECRET=...
NH_ACCOUNT_NO=...
```

## 슬래시 커맨드

```
/analyze <종목>   — 5대 투자자 기준 종목 심층 분석
/portfolio        — 포트폴리오 리밸런싱 제안
/news             — 오늘의 주요 투자 뉴스 요약
/youtube          — 머니머니코믹스 최신 인사이트
/macro            — 거시경제 현황 브리핑
```

## 기술 스택

- **AI**: Claude (Anthropic) — 5대 투자자 철학 기반 분석
- **UI**: Streamlit
- **데이터**: yfinance, 네이버 금융 RSS, YouTube RSS, BeautifulSoup
- **계좌 조회**: NH나무 OpenAPI (조회 전용)
- **패키지 관리**: uv

## 프로젝트 구조

```
BUJA/
├── app.py                          # Streamlit 진입점 (채팅 UI)
├── src/
│   └── agents/
│       ├── advisor.py              # AI 어드바이저 핵심 로직
│       └── orchestrator.py        # 슬래시 커맨드 라우팅
├── docs/
│   └── knowledge/
│       └── investors/             # 5대 투자자 철학 상세 문서
│           ├── warren_buffett.md
│           ├── benjamin_graham.md
│           ├── peter_lynch.md
│           ├── ray_dalio.md
│           └── philip_fisher.md
├── .claude/
│   ├── agents/                    # Claude 서브에이전트 정의
│   └── commands/                  # 슬래시 커맨드 정의
├── CLAUDE.md                      # AI 어드바이저 행동 원칙
└── .env.example                   # 환경변수 템플릿
```

## 면책 고지

본 서비스는 투자 참고용이며, 투자 결정과 그에 따른 책임은 전적으로 투자자 본인에게 있습니다.
