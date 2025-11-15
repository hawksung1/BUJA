# BUJA 프로젝트 개발 가이드

> **목적**: 개발 규칙, 컨벤션, 테스트 가이드를 제공하여 일관된 코드 작성

## 📋 목차
1. [코드 스타일](#코드-스타일)
2. [테스트 가이드](#테스트-가이드)
3. [UI 검증](#ui-검증)
4. [커밋 규칙](#커밋-규칙)
5. [디버깅 가이드](#디버깅-가이드)

---

## 코드 스타일

### Python 스타일 가이드
- **PEP 8** 준수
- **Black** 포맷터 사용 (권장)
- **타입 힌트** 사용 (가능한 경우)

### 네이밍 컨벤션
```python
# 클래스: PascalCase
class InvestmentAgent:
    pass

# 함수/변수: snake_case
def calculate_portfolio_value():
    user_id = 1

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 10

# 비공개: _leading_underscore
def _internal_helper():
    pass
```

### 주석 규칙
- **한국어 주석** 사용
- Docstring은 Google 스타일 권장
```python
def calculate_risk_score(user_profile: UserProfile) -> float:
    """
    사용자 프로필을 기반으로 위험 점수를 계산합니다.
    
    Args:
        user_profile: 사용자 프로필 객체
        
    Returns:
        위험 점수 (0.0 ~ 1.0)
        
    Raises:
        ValueError: 프로필 정보가 불완전한 경우
    """
    pass
```

### Import 순서
```python
# 1. 표준 라이브러리
import os
import sys
from datetime import datetime

# 2. 서드파티 라이브러리
import streamlit as st
import pandas as pd

# 3. 로컬 모듈
from src.models.user import User
from src.services.user_service import UserService
```

---

## 테스트 가이드

### 테스트 작성 원칙
1. **모든 수정/추가 시 테스트 작성 필수**
2. **단위 테스트 우선**
3. **통합 테스트는 주요 기능에 대해 작성**

### 테스트 구조
```
tests/
├── unit/                  # 단위 테스트
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/           # 통합 테스트
│   ├── test_agent_flow.py
│   └── test_api_integration.py
└── e2e/                   # E2E 테스트 (Playwright)
    └── test_user_flows.py
```

### 테스트 예시
```python
# tests/unit/test_services.py
import pytest
from src.services.portfolio_service import PortfolioService

class TestPortfolioService:
    def test_calculate_portfolio_value(self):
        """포트폴리오 가치 계산 테스트"""
        service = PortfolioService()
        portfolio = create_test_portfolio()
        
        value = service.calculate_value(portfolio)
        
        assert value > 0
        assert isinstance(value, float)
    
    def test_rebalance_recommendation(self):
        """리밸런싱 추천 테스트"""
        service = PortfolioService()
        portfolio = create_unbalanced_portfolio()
        
        recommendation = service.get_rebalance_recommendation(portfolio)
        
        assert recommendation is not None
        assert "target_allocation" in recommendation
```

### 테스트 실행
```bash
# 모든 테스트 실행
uv run test

# 특정 테스트만 실행
pytest tests/unit/test_services.py

# 커버리지 확인
pytest --cov=src tests/
```

---

## UI 검증

### Playwright 사용
- **UI 변경 시 반드시 Playwright로 검증**
- 주요 사용자 플로우 테스트

### Playwright 테스트 예시
```python
# tests/e2e/test_user_flows.py
from playwright.sync_api import Page, expect

def test_user_login_flow(page: Page):
    """사용자 로그인 플로우 테스트"""
    page.goto("http://localhost:8501")
    
    # 로그인 버튼 클릭
    page.click("text=로그인")
    
    # 로그인 폼 입력
    page.fill("input[name='username']", "test_user")
    page.fill("input[name='password']", "test_password")
    page.click("button:has-text('로그인')")
    
    # 로그인 성공 확인
    expect(page.locator("text=환영합니다")).to_be_visible()
```

### Playwright 실행
```bash
# Playwright 설치 (최초 1회)
playwright install

# 테스트 실행
playwright test

# UI 모드로 실행
playwright test --ui
```

---

## 커밋 규칙

### 커밋 메시지 형식
```
<type>: <subject>

<body>

<footer>
```

### Type 종류
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

### 예시
```
feat: 투자 성향 분석 기능 추가

- 사용자 설문 기반 투자 성향 분석
- 위험 감수 성향 정량적 측정
- 투자 성향 저장 기능

Closes #123
```

---

## 디버깅 가이드

### 로깅
```python
import logging

# 로거 설정
logger = logging.getLogger(__name__)

# 로그 레벨
logger.debug("상세 디버그 정보")
logger.info("일반 정보")
logger.warning("경고 메시지")
logger.error("오류 발생")
logger.critical("심각한 오류")
```

### Streamlit 디버깅
```python
# Streamlit 디버그 모드
import streamlit as st

# 디버그 정보 표시
if st.sidebar.checkbox("디버그 모드"):
    st.write("디버그 정보:", debug_data)
```

### 일반적인 문제 해결

#### 1. LLM API 오류
- API 키 확인
- 요청 제한 확인
- 네트워크 연결 확인

#### 2. 데이터베이스 연결 오류
- 연결 설정 확인
- 권한 확인
- 데이터베이스 상태 확인

#### 3. 의존성 문제
```bash
# 의존성 재설치
uv sync

# 특정 패키지 재설치
uv pip install --force-reinstall package_name
```

---

## 코드 리뷰 체크리스트

### 필수 확인 사항
- [ ] 테스트 코드 작성/업데이트
- [ ] UI 변경 시 Playwright 테스트 추가
- [ ] 타입 힌트 추가 (가능한 경우)
- [ ] Docstring 작성
- [ ] 에러 처리 구현
- [ ] 로깅 추가 (필요한 경우)
- [ ] 보안 고려사항 확인
- [ ] **가이드 파일 업데이트** ⚠️ (구조/규칙 변경 시)

### 가이드 업데이트 체크리스트
작업 완료 후 다음을 확인하고 필요한 가이드를 업데이트하세요:

- [ ] 새로운 디렉토리 추가 → `ARCHITECTURE.md` 업데이트
- [ ] 새로운 파일 추가 → `CURSOR_GUIDE.md` 업데이트
- [ ] 새로운 모듈/서비스 추가 → `ARCHITECTURE.md` 업데이트
- [ ] 아키텍처 변경 → `ARCHITECTURE.md` 업데이트
- [ ] 개발 규칙 변경 → `DEVELOPMENT.md` 업데이트
- [ ] 설정 파일 변경 → `DEVELOPMENT.md` 업데이트

**상세 가이드**: `.cursor/GUIDE_UPDATE.md` 참조

### 코드 품질
- [ ] PEP 8 준수
- [ ] 중복 코드 제거
- [ ] 함수/클래스 크기 적절
- [ ] 네이밍 명확

---

## 참고사항

### 관련 가이드
- 프로젝트 가이드: `.cursor/CURSOR_GUIDE.md`
- 아키텍처 가이드: `.cursor/ARCHITECTURE.md`

### 도구
- **포맷터**: Black
- **린터**: flake8, pylint
- **타입 체커**: mypy (선택)
- **테스트**: pytest
- **E2E 테스트**: Playwright

### 설정 파일
- `pyproject.toml`: 프로젝트 설정 및 의존성
- `.pylintrc`: 린터 설정 (향후 추가)
- `pytest.ini`: 테스트 설정 (향후 추가)

