# BUJA 프로젝트 아키텍처 가이드

> **목적**: 프로젝트의 구조와 설계 원칙을 이해하여 최소한의 context로 작업할 수 있도록 함

## 📋 목차
1. [전체 아키텍처](#전체-아키텍처)
2. [모듈 구조](#모듈-구조)
3. [데이터 흐름](#데이터-흐름)
4. [주요 컴포넌트](#주요-컴포넌트)
5. [확장 포인트](#확장-포인트)

---

## 전체 아키텍처

### 레이어 구조
```
┌─────────────────────────────────────┐
│     Presentation Layer (Streamlit)  │
│         app.py, pages/              │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│      Business Logic Layer           │
│      src/services/                  │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│      Agent Layer                    │
│      src/agents/                    │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│      Data Layer                     │
│      src/models/, src/database/     │
└─────────────────────────────────────┘
```

### 핵심 원칙
1. **계층 분리**: Presentation → Business → Agent → Data
2. **모듈화**: 각 기능은 독립적인 모듈로 구성
3. **확장성**: 새로운 LLM 제공자, 데이터 소스 추가 용이
4. **테스트 가능**: 각 레이어 독립 테스트 가능

---

## 모듈 구조

### 예상 모듈 구조 (향후 구현)

```
src/
├── __init__.py
├── agents/                    # LLM Agent 모듈
│   ├── __init__.py
│   ├── base_agent.py         # 기본 Agent 클래스
│   ├── investment_agent.py   # 투자 상담 Agent
│   └── portfolio_agent.py    # 포트폴리오 분석 Agent
├── models/                      # 데이터 모델
│   ├── __init__.py
│   ├── user.py                # 사용자 모델
│   ├── portfolio.py           # 포트폴리오 모델
│   ├── investment.py          # 투자 기록 모델
│   └── recommendation.py      # 추천 모델
├── services/                    # 비즈니스 로직
│   ├── __init__.py
│   ├── user_service.py        # 사용자 관리 서비스
│   ├── portfolio_service.py   # 포트폴리오 관리 서비스
│   ├── recommendation_service.py  # 추천 서비스
│   └── analysis_service.py    # 분석 서비스
├── utils/                       # 유틸리티
│   ├── __init__.py
│   ├── llm_client.py          # LLM API 클라이언트
│   ├── vision_client.py       # Vision API 클라이언트
│   ├── data_loader.py         # 데이터 로더
│   └── validators.py          # 검증 유틸리티
└── database/                    # 데이터베이스 관련
    ├── __init__.py
    ├── connection.py          # DB 연결
    └── repositories.py        # 데이터 접근 레이어
```

### 현재 상태
- `src/` 디렉토리만 존재 (초기 단계)
- 모듈 구조는 향후 구현 예정
- **참고**: 상세한 설계는 `docs/DESIGN.md` 파일 참조 (1719줄)

---

## 데이터 흐름

### 1. 사용자 투자 상담 흐름
```
사용자 입력 (Streamlit)
    ↓
Investment Agent (LLM)
    ↓
투자 성향 분석
    ↓
자산 배분 추천 생성
    ↓
추천 근거 생성
    ↓
사용자에게 표시
```

### 2. 스크린샷 분석 흐름
```
스크린샷 업로드
    ↓
Vision API (이미지 분석)
    ↓
포트폴리오 정보 추출
    ↓
Portfolio Agent (분석)
    ↓
분석 결과 및 제안
    ↓
데이터 저장
```

### 3. 자산 변동 추적 흐름
```
시장 데이터 수집
    ↓
포트폴리오 가치 계산
    ↓
변동 분석
    ↓
리밸런싱 필요 여부 판단
    ↓
알림/추천 생성
```

---

## 주요 컴포넌트

### 1. LLM Agent 시스템
- **위치**: `src/agents/`
- **책임**: 
  - 사용자와의 대화형 인터페이스
  - 투자 상담 및 추천 생성
  - 포트폴리오 분석
- **확장성**: 여러 LLM 제공자 지원 (OpenAI, Anthropic, Google 등)

### 2. 사용자 관리
- **위치**: `src/services/user_service.py`
- **책임**:
  - 계정 생성/관리
  - KYC 정보 관리
  - 투자 성향 저장/업데이트
  - 재무 상황 관리

### 3. 포트폴리오 관리
- **위치**: `src/services/portfolio_service.py`
- **책임**:
  - 자산 배분 계산
  - 리밸런싱 제안
  - 성과 분석
  - 리스크 측정

### 4. 추천 시스템
- **위치**: `src/services/recommendation_service.py`
- **책임**:
  - 투자 성향 기반 추천
  - 자산 배분 모델 적용 (MPT, Black-Litterman 등)
  - 추천 근거 생성

### 5. 데이터 저장
- **위치**: `src/database/`
- **책임**:
  - 사용자 데이터 저장
  - 투자 기록 저장
  - 시장 데이터 저장
  - 분석 결과 저장

---

## 확장 포인트

### 1. 새로운 LLM 제공자 추가
- `src/utils/llm_client.py`에 새로운 클라이언트 추가
- `src/agents/base_agent.py`에서 통합 인터페이스 사용

### 2. 새로운 데이터 소스 추가
- `src/utils/data_loader.py`에 새로운 로더 추가
- 표준 인터페이스 준수

### 3. 자동 구매 기능 (향후)
- `src/services/auto_trade_service.py` 추가
- API 인터페이스는 이미 설계됨 (REQ-051 ~ REQ-057)

### 4. 브로커 연동 (향후)
- `src/integrations/brokers/` 디렉토리 추가
- 각 브로커별 모듈로 분리

---

## 설계 원칙

### 1. 단일 책임 원칙
- 각 모듈은 하나의 책임만 가짐
- 예: `user_service.py`는 사용자 관리만 담당

### 2. 의존성 역전
- 상위 레이어가 하위 레이어에 의존하지 않음
- 인터페이스를 통한 추상화

### 3. 확장에 열려있고 수정에 닫혀있음
- 새로운 기능 추가 시 기존 코드 수정 최소화
- 인터페이스 기반 설계

### 4. 테스트 가능성
- 각 모듈은 독립적으로 테스트 가능
- Mock 객체 활용 용이

---

## 참고사항

### 요구사항 문서
- 상세 요구사항: `REQUIREMENTS.md`
- 아키텍처 관련 요구사항:
  - REQ-068: 모듈화된 아키텍처
  - REQ-069: 새로운 LLM 제공자 추가 용이
  - REQ-070: 새로운 데이터 소스 추가 용이

### 개발 가이드
- 개발 규칙: `.cursor/DEVELOPMENT.md`
- 프로젝트 가이드: `.cursor/CURSOR_GUIDE.md`

