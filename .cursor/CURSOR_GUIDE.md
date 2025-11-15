# BUJA 프로젝트 - Cursor 작업 가이드

> **⚠️ 중요**: 이 파일은 Cursor AI가 작업을 시작할 때 항상 참조해야 하는 핵심 가이드입니다.

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [빠른 참조](#빠른-참조)
3. [작업 흐름](#작업-흐름)
4. [파일 구조](#파일-구조)
5. [관련 가이드](#관련-가이드)

---

## 프로젝트 개요

### 프로젝트명
**BUJA** - LLM 기반 자산 관리 및 투자 제안 시스템

### 핵심 기능
- LLM Agent를 통한 대화형 투자 상담
- 사용자 투자 성향 분석 및 저장
- 맞춤형 자산 배분 추천
- 투자 기록 관리 및 성과 분석
- 스크린샷 기반 자산 분석 (Vision API)
- 동적 데이터 반영 (시장 트랜드, 자산 변동)

### 기술 스택
- **언어**: Python 3.10+
- **웹 프레임워크**: Streamlit
- **패키지 관리**: uv
- **개발 환경**: WSL (Windows Subsystem for Linux)

---

## 빠른 참조

### 주요 파일 위치
| 파일/디렉토리 | 용도 | 참고 |
|-------------|------|------|
| `app.py` | Streamlit 메인 앱 | 시작점 |
| `src/` | 소스 코드 모듈 | 핵심 로직 |
| `pages/` | Streamlit 멀티 페이지 | UI 페이지 |
| `data/` | 데이터 파일 | 저장 데이터 |
| `config/` | 설정 파일 | 환경 변수, DB 설정 |
| `tests/` | 테스트 코드 | 단위/통합/E2E 테스트 |
| `pyproject.toml` | 프로젝트 설정 | 의존성 관리 |
| `docs/REQUIREMENTS.md` | 상세 요구사항 | **503줄 - 참조용** |
| `docs/DESIGN.md` | 상세 설계 문서 | **1719줄 - 아키텍처 참조** |

### 주요 명령어
```bash
# 개발 서버 실행
uv run dev

# 의존성 설치
uv sync

# 테스트 실행
uv run test
```

### 요구사항 문서
- `REQUIREMENTS.md`: 전체 요구사항 (503줄)
  - **주의**: 전체를 읽지 말고 필요한 부분만 참조
  - 주요 섹션:
    - 2.1: LLM Agent 시스템
    - 2.2: 사용자 계정 관리
    - 2.3: 투자 성향 관리
    - 2.4: 자산 배분 추천
    - 2.5: 투자 기록 관리
    - 2.9: 스크린샷 기반 분석

---

## 작업 흐름

### 1. 작업 시작 전
1. ✅ `.cursorrules` 확인
2. ✅ 관련 가이드 파일 확인 (`.cursor/` 디렉토리)
3. ✅ 작업 범위 파악

### 2. 코드 작업 시
1. **최소한의 파일만 읽기**
   - 필요한 모듈만 import
   - 관련 파일만 검색/읽기
   - 큰 파일(REQUIREMENTS.md 등)은 필요한 섹션만 참조

2. **코드 작성 규칙**
   - 한국어 주석 및 문서
   - 테스트 코드 작성 필수
   - UI 변경 시 Playwright 검증

3. **파일 수정 시**
   - 관련 테스트 업데이트
   - 변경 사항 문서화

### 3. 작업 완료 후
1. 테스트 실행
2. 린터 오류 확인
3. UI 변경 시 Playwright 검증

---

## 파일 구조

### 현재 구조
```
BUJA/
├── app.py                  # Streamlit 메인 앱
├── pages/                  # Streamlit 멀티 페이지 (현재 비어있음)
├── src/                    # 소스 코드
│   └── __init__.py
├── data/                   # 데이터 파일 (현재 비어있음)
├── .cursor/                # Cursor 가이드 파일
│   ├── CURSOR_GUIDE.md    # 이 파일
│   ├── ARCHITECTURE.md    # 아키텍처 가이드
│   └── DEVELOPMENT.md     # 개발 가이드
├── pyproject.toml          # 프로젝트 설정
├── REQUIREMENTS.md         # 상세 요구사항 (503줄)
├── README.md               # 프로젝트 README
└── .cursorrules            # Cursor 자동 읽기 파일
```

### 예상 구조 (향후)
```
BUJA/
├── app.py
├── pages/
│   ├── home.py
│   ├── portfolio.py
│   └── settings.py
├── src/
│   ├── agents/            # LLM Agent 모듈
│   ├── models/            # 데이터 모델
│   ├── services/            # 비즈니스 로직
│   ├── utils/             # 유틸리티
│   └── database/          # 데이터베이스 관련
├── data/
│   ├── users/             # 사용자 데이터
│   └── market/            # 시장 데이터
└── tests/                 # 테스트 코드
```

---

## 관련 가이드

### 필수 읽기 가이드
1. **`.cursor/ARCHITECTURE.md`**
   - 프로젝트 아키텍처
   - 모듈 구조 및 책임
   - 데이터 흐름

2. **`.cursor/DEVELOPMENT.md`**
   - 개발 규칙 및 컨벤션
   - 테스트 작성 가이드
   - 코드 리뷰 체크리스트

3. **`.cursor/GUIDE_UPDATE.md`** ⚠️
   - 가이드 파일 업데이트 가이드라인
   - 작업 후 가이드 업데이트 체크리스트
   - 가이드별 업데이트 방법

### 참고 문서
- `docs/REQUIREMENTS.md`: 상세 요구사항 (필요한 부분만 참조)
- `docs/DESIGN.md`: 상세 설계 문서 (아키텍처, DB 설계 등)
- `docs/WBS.md`: 프로젝트 작업 분해 구조
- `README.md`: 프로젝트 설정 및 실행 가이드

---

## 주의사항

### ⚠️ Context 관리
- **REQUIREMENTS.md는 503줄** - 전체를 읽지 말고 필요한 섹션만 참조
- 큰 파일은 필요한 부분만 읽기
- 관련 없는 파일은 읽지 않기

### ✅ 작업 원칙
1. 최소한의 context로 작업
2. 테스트 코드 필수
3. UI 변경 시 Playwright 검증
4. 한국어 응답 및 주석
5. Context7 MCP 활용

### 📝 문서화 및 가이드 업데이트
- 중요한 결정사항은 가이드 파일에 반영
- 새로운 모듈 추가 시 ARCHITECTURE.md 업데이트
- 개발 규칙 변경 시 DEVELOPMENT.md 업데이트
- **작업 완료 후 구조/규칙 변경 시 가이드 파일 업데이트 필수** ⚠️
- **가이드 업데이트 가이드라인**: `.cursor/GUIDE_UPDATE.md` 참조

---

## 빠른 문제 해결

### 프로젝트 실행 안 됨
→ `README.md`의 "프로젝트 설정" 섹션 확인

### 의존성 문제
→ `pyproject.toml` 확인 후 `uv sync` 실행

### 요구사항 확인 필요
→ `docs/REQUIREMENTS.md`에서 해당 섹션만 검색/참조

### 아키텍처 이해 필요
→ `.cursor/ARCHITECTURE.md` 참조

### 개발 규칙 확인
→ `.cursor/DEVELOPMENT.md` 참조

