# BUJA 프로젝트 프로그램 설계서

## 1. 시스템 개요

### 1.1 프로젝트 목적
BUJA는 LLM 기반 자산 관리 및 투자 제안 시스템으로, 사용자의 투자 성향을 학습하고 맞춤형 자산 배분을 추천하는 지능형 플랫폼입니다.

### 1.2 주요 기능
- LLM Agent 기반 대화형 투자 상담
- 사용자 투자 성향 분석 및 관리
- 목표 기반 투자 계획 수립
- 자산 배분 추천 및 리밸런싱 제안
- 스크린샷 기반 포트폴리오 분석
- 투자 기록 관리 및 성과 분석
- 리스크 관리 및 평가

### 1.3 시스템 특성
- **대화형 인터페이스**: LLM Agent를 통한 자연어 상호작용
- **맞춤형 추천**: 사용자별 투자 성향 및 재무 상황 기반
- **실시간 분석**: 시장 데이터 및 트랜드 반영
- **확장 가능**: 자동 구매 기능 등 향후 확장 고려

---

## 2. 시스템 아키텍처

### 2.1 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Streamlit  │  │   Web UI     │  │  Mobile Web   │     │
│  │   App UI    │  │  (React)     │  │  (Responsive) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Agent      │  │  Portfolio   │  │  Screenshot  │     │
│  │  Service     │  │  Service     │  │  Analyzer    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  User        │  │  Investment  │  │  Risk        │     │
│  │  Service     │  │  Service     │  │  Manager     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Asset       │  │  Rebalancing │  │  Performance │     │
│  │  Allocation  │  │  Strategy    │  │  Analyzer    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Portfolio   │  │  Goal        │  │  Trend       │     │
│  │  Optimizer   │  │  Planner     │  │  Analyzer    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Access Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Database   │  │   Cache      │  │   File      │     │
│  │   Repository │  │   (Redis)    │  │   Storage   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      External Services                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  LLM API     │  │  Financial   │  │  News        │     │
│  │  (OpenAI,    │  │  Data API    │  │  Crawler     │     │
│  │   Claude)    │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 계층 구조

#### 2.2.1 Presentation Layer (표현 계층)
- **Streamlit UI**: 메인 웹 인터페이스
- **페이지 구조**:
  - 홈/대시보드
  - Agent 채팅
  - 포트폴리오 분석
  - 투자 기록
  - 설정

#### 2.2.2 Application Layer (애플리케이션 계층)
- **Agent Service**: LLM Agent 관리 및 대화 처리
- **Portfolio Service**: 포트폴리오 관리 및 분석
- **User Service**: 사용자 관리 및 인증
- **Investment Service**: 투자 기록 관리
- **Screenshot Analyzer**: 이미지 분석 및 정보 추출

#### 2.2.3 Business Logic Layer (비즈니스 로직 계층)
- **Asset Allocation**: 자산 배분 알고리즘
- **Portfolio Optimizer**: 포트폴리오 최적화 (MPT, Black-Litterman)
- **Rebalancing Strategy**: 리밸런싱 전략
- **Risk Manager**: 리스크 측정 및 관리
- **Goal Planner**: 목표 기반 계획 수립
- **Performance Analyzer**: 성과 분석

#### 2.2.4 Data Access Layer (데이터 접근 계층)
- **Repository Pattern**: 데이터베이스 추상화
- **Cache Layer**: Redis를 통한 캐싱
- **File Storage**: 이미지 및 파일 저장

#### 2.2.5 External Services (외부 서비스)
- **LLM APIs**: OpenAI, Anthropic, Google 등
- **Financial Data APIs**: 주가, 환율, 경제 지표
- **News Services**: 뉴스 크롤링 및 분석

---

## 3. 기술 스택

### 3.1 Backend
- **언어**: Python 3.10+
- **프레임워크**: 
  - Streamlit (웹 UI)
  - FastAPI (향후 REST API 확장)
- **비동기 처리**: asyncio, aiohttp
- **데이터 처리**: pandas, numpy

### 3.2 LLM & AI
- **LLM 라이브러리**:
  - openai (GPT-4, GPT-4 Vision)
  - anthropic (Claude, Claude Vision)
  - langchain (Agent 프레임워크)
- **이미지 처리**: PIL/Pillow, OpenCV

### 3.3 데이터베이스
- **주 데이터베이스**: PostgreSQL
- **캐시**: Redis
- **ORM**: SQLAlchemy
- **마이그레이션**: Alembic

### 3.4 인증 및 보안
- **인증**: bcrypt (비밀번호 해싱)
- **세션 관리**: Streamlit Session State
- **암호화**: cryptography

### 3.5 외부 API 연동
- **HTTP 클라이언트**: httpx, requests
- **금융 데이터**: yfinance, pykrx (한국 주식)

### 3.6 테스트
- **단위 테스트**: pytest
- **통합 테스트**: pytest-asyncio
- **Mock**: unittest.mock, pytest-mock

### 3.7 배포 및 인프라
- **컨테이너**: Docker
- **패키지 관리**: uv
- **환경 관리**: python-dotenv

---

## 4. 데이터베이스 설계

### 4.1 ERD (Entity Relationship Diagram)

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    User      │         │   Profile    │         │  Financial   │
│──────────────│         │──────────────│         │  Situation   │
│ id (PK)      │────────>│ id (PK)      │         │──────────────│
│ email        │   1:1   │ user_id (FK) │   1:1   │ id (PK)      │
│ password_hash│         │ name         │         │ user_id (FK) │
│ created_at   │         │ age          │         │ monthly_income│
│ updated_at   │         │ updated_at   │         │ monthly_expense│
└──────────────┘         └──────────────┘         │ total_assets │
                                                    │ total_debt   │
┌──────────────┐         ┌──────────────┐         │ updated_at   │
│  Investment  │         │  Investment  │         └──────────────┘
│  Preference  │         │   Record     │
│──────────────│         │──────────────│         ┌──────────────┐
│ id (PK)      │         │ id (PK)      │         │  Financial   │
│ user_id (FK) │   1:1   │ user_id (FK) │   N:1   │    Goal      │
│ risk_tolerance│        │ asset_type   │         │──────────────│
│ target_return│         │ symbol       │         │ id (PK)      │
│ investment_period│      │ quantity     │         │ user_id (FK) │
│ updated_at   │         │ buy_price    │         │ goal_type    │
└──────────────┘         │ sell_price   │         │ target_amount│
                         │ buy_date     │         │ target_date  │
┌──────────────┐         │ sell_date    │         │ priority     │
│  Portfolio   │         │ profit_loss  │         │ created_at   │
│  Analysis    │         │ created_at   │         └──────────────┘
│──────────────│         └──────────────┘
│ id (PK)      │
│ user_id (FK) │   N:1   ┌──────────────┐
│ screenshot_id│        │  Screenshot   │
│ analysis_date│         │──────────────│
│ asset_allocation│      │ id (PK)      │
│ risk_level   │         │ user_id (FK) │
│ performance  │         │ file_path    │
│ created_at   │         │ app_type     │
└──────────────┘         │ extracted_data│
                         │ created_at   │
                         └──────────────┘
```

### 4.2 주요 테이블 설계

#### 4.2.1 users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 4.2.2 user_profiles
```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    name VARCHAR(100),
    age INTEGER,
    occupation VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.3 financial_situations
```sql
CREATE TABLE financial_situations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    monthly_income DECIMAL(15, 2),
    monthly_expense DECIMAL(15, 2),
    total_assets DECIMAL(15, 2),
    total_debt DECIMAL(15, 2),
    emergency_fund DECIMAL(15, 2),
    family_members INTEGER,
    insurance_coverage DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.4 investment_preferences
```sql
CREATE TABLE investment_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    risk_tolerance INTEGER NOT NULL, -- 1-10 scale
    target_return DECIMAL(5, 2),
    investment_period VARCHAR(20), -- SHORT, MEDIUM, LONG
    preferred_asset_types TEXT[], -- ['STOCK', 'BOND', 'REAL_ESTATE']
    max_loss_tolerance DECIMAL(5, 2), -- percentage
    investment_experience VARCHAR(20), -- BEGINNER, INTERMEDIATE, ADVANCED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.5 financial_goals
```sql
CREATE TABLE financial_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    goal_type VARCHAR(50) NOT NULL, -- RETIREMENT, HOUSE, EDUCATION, etc.
    target_amount DECIMAL(15, 2) NOT NULL,
    target_date DATE NOT NULL,
    priority INTEGER NOT NULL,
    current_progress DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.6 investment_records
```sql
CREATE TABLE investment_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    asset_type VARCHAR(50) NOT NULL, -- STOCK, BOND, FUND, etc.
    symbol VARCHAR(50),
    quantity DECIMAL(15, 4) NOT NULL,
    buy_price DECIMAL(15, 2) NOT NULL,
    sell_price DECIMAL(15, 2),
    buy_date DATE NOT NULL,
    sell_date DATE,
    fees DECIMAL(15, 2) DEFAULT 0,
    taxes DECIMAL(15, 2) DEFAULT 0,
    dividend_interest DECIMAL(15, 2) DEFAULT 0,
    profit_loss DECIMAL(15, 2),
    realized BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.7 screenshots
```sql
CREATE TABLE screenshots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    app_type VARCHAR(50), -- KEYUM, NH, UPBIT, etc.
    extracted_data JSONB,
    analysis_status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED, FAILED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

#### 4.2.8 portfolio_analyses
```sql
CREATE TABLE portfolio_analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    screenshot_id INTEGER REFERENCES screenshots(id),
    analysis_date DATE NOT NULL,
    total_value DECIMAL(15, 2),
    asset_allocation JSONB, -- {stock: 60%, bond: 30%, cash: 10%}
    risk_level VARCHAR(20),
    diversification_score DECIMAL(5, 2),
    performance_metrics JSONB, -- {sharpe_ratio, beta, alpha, etc.}
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.9 asset_recommendations
```sql
CREATE TABLE asset_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    recommendation_type VARCHAR(50), -- INITIAL, REBALANCE, GOAL_BASED
    target_allocation JSONB,
    reasoning TEXT,
    risk_assessment TEXT,
    expected_return DECIMAL(5, 2),
    confidence_score DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

#### 4.2.10 rebalancing_history
```sql
CREATE TABLE rebalancing_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    recommendation_id INTEGER REFERENCES asset_recommendations(id),
    before_allocation JSONB,
    after_allocation JSONB,
    rebalancing_cost DECIMAL(15, 2),
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. 모듈 구조

### 5.1 프로젝트 디렉토리 구조

```
BUJA/
├── app.py                      # Streamlit 메인 앱
├── config/
│   ├── __init__.py
│   ├── settings.py            # 설정 관리
│   └── database.py            # DB 연결 설정
├── src/
│   ├── __init__.py
│   ├── agents/                 # LLM Agent 모듈
│   │   ├── __init__.py
│   │   ├── base_agent.py      # Agent 기본 클래스
│   │   ├── investment_agent.py # 투자 상담 Agent
│   │   └── llm_providers.py   # LLM 제공자 추상화
│   ├── services/               # 비즈니스 로직 서비스
│   │   ├── __init__.py
│   │   ├── user_service.py     # 사용자 관리
│   │   ├── portfolio_service.py # 포트폴리오 관리
│   │   ├── investment_service.py # 투자 기록 관리
│   │   ├── screenshot_service.py # 스크린샷 분석
│   │   └── recommendation_service.py # 추천 서비스
│   ├── models/                 # 데이터 모델
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   ├── investment.py
│   │   └── recommendation.py
│   ├── repositories/           # 데이터 접근 계층
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── user_repository.py
│   │   ├── portfolio_repository.py
│   │   └── investment_repository.py
│   ├── analyzers/              # 분석 엔진
│   │   ├── __init__.py
│   │   ├── portfolio_analyzer.py
│   │   ├── risk_analyzer.py
│   │   ├── performance_analyzer.py
│   │   └── asset_allocator.py
│   ├── optimizers/             # 최적화 알고리즘
│   │   ├── __init__.py
│   │   ├── mpt_optimizer.py   # Modern Portfolio Theory
│   │   └── black_litterman.py  # Black-Litterman Model
│   ├── utils/                  # 유틸리티
│   │   ├── __init__.py
│   │   ├── security.py         # 보안 관련
│   │   ├── validators.py       # 검증
│   │   └── formatters.py       # 포맷팅
│   └── external/               # 외부 API 연동
│       ├── __init__.py
│       ├── llm_client.py      # LLM API 클라이언트
│       ├── financial_data.py  # 금융 데이터 API
│       └── news_crawler.py    # 뉴스 크롤러
├── pages/                      # Streamlit 페이지
│   ├── __init__.py
│   ├── home.py
│   ├── agent_chat.py
│   ├── portfolio.py
│   ├── investments.py
│   └── settings.py
├── data/                       # 데이터 파일
├── tests/                      # 테스트
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── migrations/                 # DB 마이그레이션
├── .env.example                # 환경 변수 예제
├── pyproject.toml
├── README.md
├── REQUIREMENTS.md
└── DESIGN.md
```

### 5.2 주요 모듈 상세 설계

#### 5.2.1 Agent 모듈

**base_agent.py**
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseAgent(ABC):
    """Agent 기본 클래스"""
    
    def __init__(self, llm_provider: str, api_key: str):
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.conversation_history = []
    
    @abstractmethod
    async def chat(self, message: str, context: Dict[str, Any]) -> str:
        """사용자 메시지에 대한 응답 생성"""
        pass
    
    @abstractmethod
    async def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """이미지 분석"""
        pass
```

**investment_agent.py**
```python
from src.agents.base_agent import BaseAgent
from src.services.portfolio_service import PortfolioService
from src.services.recommendation_service import RecommendationService

class InvestmentAgent(BaseAgent):
    """투자 상담 Agent"""
    
    def __init__(self, llm_provider: str, api_key: str):
        super().__init__(llm_provider, api_key)
        self.portfolio_service = PortfolioService()
        self.recommendation_service = RecommendationService()
    
    async def chat(self, message: str, context: Dict[str, Any]) -> str:
        """투자 관련 질문에 대한 답변"""
        # 사용자 포트폴리오 정보 가져오기
        # LLM에 컨텍스트와 함께 전달
        # 응답 생성 및 반환
        pass
    
    async def analyze_portfolio_screenshot(self, image_path: str, user_id: int) -> Dict[str, Any]:
        """포트폴리오 스크린샷 분석"""
        # Vision API로 이미지 분석
        # 정보 추출
        # 포트폴리오 평가
        pass
```

#### 5.2.2 Service 모듈

**portfolio_service.py**
```python
from src.repositories.portfolio_repository import PortfolioRepository
from src.analyzers.portfolio_analyzer import PortfolioAnalyzer
from src.analyzers.risk_analyzer import RiskAnalyzer

class PortfolioService:
    """포트폴리오 관리 서비스"""
    
    def __init__(self):
        self.repository = PortfolioRepository()
        self.analyzer = PortfolioAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
    
    async def analyze_portfolio(self, user_id: int) -> Dict[str, Any]:
        """포트폴리오 분석"""
        portfolio = await self.repository.get_user_portfolio(user_id)
        analysis = await self.analyzer.analyze(portfolio)
        risk_assessment = await self.risk_analyzer.assess(portfolio)
        return {
            'analysis': analysis,
            'risk': risk_assessment
        }
    
    async def get_rebalancing_suggestion(self, user_id: int) -> Dict[str, Any]:
        """리밸런싱 제안"""
        pass
```

#### 5.2.3 Analyzer 모듈

**portfolio_analyzer.py**
```python
import pandas as pd
from typing import Dict, Any

class PortfolioAnalyzer:
    """포트폴리오 분석기"""
    
    async def analyze(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """포트폴리오 종합 분석"""
        return {
            'total_value': self._calculate_total_value(portfolio),
            'asset_allocation': self._calculate_allocation(portfolio),
            'diversification_score': self._calculate_diversification(portfolio),
            'performance': self._calculate_performance(portfolio)
        }
    
    def _calculate_total_value(self, portfolio: Dict) -> float:
        """총 자산 가치 계산"""
        pass
    
    def _calculate_allocation(self, portfolio: Dict) -> Dict[str, float]:
        """자산 배분 비율 계산"""
        pass
    
    def _calculate_diversification(self, portfolio: Dict) -> float:
        """다각화 점수 계산"""
        pass
```

**risk_analyzer.py**
```python
import numpy as np
from typing import Dict, Any

class RiskAnalyzer:
    """리스크 분석기"""
    
    async def assess(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """리스크 평가"""
        return {
            'var': self._calculate_var(portfolio),
            'cvar': self._calculate_cvar(portfolio),
            'volatility': self._calculate_volatility(portfolio),
            'beta': self._calculate_beta(portfolio),
            'max_drawdown': self._calculate_max_drawdown(portfolio)
        }
    
    def _calculate_var(self, portfolio: Dict, confidence: float = 0.95) -> float:
        """Value at Risk 계산"""
        pass
    
    def _calculate_cvar(self, portfolio: Dict, confidence: float = 0.95) -> float:
        """Conditional VaR 계산"""
        pass
```

#### 5.2.4 Optimizer 모듈

**mpt_optimizer.py**
```python
import numpy as np
import pandas as pd
from scipy.optimize import minimize

class MPTOptimizer:
    """Modern Portfolio Theory 최적화"""
    
    def optimize(self, expected_returns: np.ndarray, 
                 cov_matrix: np.ndarray,
                 risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """효율적 프론티어 계산 및 최적 포트폴리오 찾기"""
        # 효율적 프론티어 계산
        # 최대 샤프 비율 포트폴리오 찾기
        pass
    
    def calculate_efficient_frontier(self, expected_returns: np.ndarray,
                                    cov_matrix: np.ndarray) -> pd.DataFrame:
        """효율적 프론티어 계산"""
        pass
```

---

## 6. API 설계

### 6.1 내부 API (Service Layer)

#### 6.1.1 UserService API

```python
class UserService:
    async def create_user(email: str, password: str, profile_data: Dict) -> User
    async def authenticate_user(email: str, password: str) -> Optional[User]
    async def get_user_profile(user_id: int) -> UserProfile
    async def update_user_profile(user_id: int, profile_data: Dict) -> UserProfile
    async def get_financial_situation(user_id: int) -> FinancialSituation
    async def update_financial_situation(user_id: int, data: Dict) -> FinancialSituation
```

#### 6.1.2 PortfolioService API

```python
class PortfolioService:
    async def analyze_portfolio(user_id: int) -> PortfolioAnalysis
    async def get_current_allocation(user_id: int) -> Dict[str, float]
    async def calculate_performance(user_id: int, period: str) -> PerformanceMetrics
    async def get_rebalancing_suggestion(user_id: int) -> RebalancingSuggestion
```

#### 6.1.3 InvestmentService API

```python
class InvestmentService:
    async def create_investment_record(user_id: int, record_data: Dict) -> InvestmentRecord
    async def get_investment_records(user_id: int, filters: Dict) -> List[InvestmentRecord]
    async def update_investment_record(record_id: int, data: Dict) -> InvestmentRecord
    async def calculate_total_performance(user_id: int) -> PerformanceSummary
```

#### 6.1.4 ScreenshotService API

```python
class ScreenshotService:
    async def upload_screenshot(user_id: int, file_path: str, app_type: str) -> Screenshot
    async def analyze_screenshot(screenshot_id: int) -> PortfolioAnalysis
    async def extract_portfolio_data(image_path: str) -> Dict[str, Any]
    async def delete_screenshot(screenshot_id: int) -> bool
```

#### 6.1.5 RecommendationService API

```python
class RecommendationService:
    async def generate_recommendation(user_id: int, recommendation_type: str) -> AssetRecommendation
    async def get_recommendation_history(user_id: int) -> List[AssetRecommendation]
    async def explain_recommendation(recommendation_id: int) -> str
```

### 6.2 외부 API (향후 REST API 확장)

#### 6.2.1 Authentication Endpoints

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
```

#### 6.2.2 User Endpoints

```
GET    /api/v1/users/me
PUT    /api/v1/users/me
GET    /api/v1/users/me/profile
PUT    /api/v1/users/me/profile
GET    /api/v1/users/me/financial-situation
PUT    /api/v1/users/me/financial-situation
```

#### 6.2.3 Portfolio Endpoints

```
GET    /api/v1/portfolio
GET    /api/v1/portfolio/analysis
GET    /api/v1/portfolio/performance
GET    /api/v1/portfolio/rebalancing-suggestion
```

#### 6.2.4 Investment Endpoints

```
GET    /api/v1/investments
POST   /api/v1/investments
GET    /api/v1/investments/{id}
PUT    /api/v1/investments/{id}
DELETE /api/v1/investments/{id}
GET    /api/v1/investments/performance
```

#### 6.2.5 Screenshot Endpoints

```
POST   /api/v1/screenshots/upload
GET    /api/v1/screenshots
GET    /api/v1/screenshots/{id}
POST   /api/v1/screenshots/{id}/analyze
DELETE /api/v1/screenshots/{id}
```

#### 6.2.6 Recommendation Endpoints

```
POST   /api/v1/recommendations
GET    /api/v1/recommendations
GET    /api/v1/recommendations/{id}
GET    /api/v1/recommendations/{id}/explanation
```

#### 6.2.7 Agent Endpoints

```
POST   /api/v1/agent/chat
POST   /api/v1/agent/analyze-image
GET    /api/v1/agent/conversation-history
```

---

## 7. 클래스 설계

### 7.1 핵심 클래스 다이어그램

```
┌─────────────────────┐
│   InvestmentAgent   │
├─────────────────────┤
│ - llm_provider      │
│ - conversation_history│
├─────────────────────┤
│ + chat()            │
│ + analyze_image()   │
│ + analyze_portfolio()│
└──────────┬──────────┘
           │
           │ uses
           ▼
┌─────────────────────┐
│   LLMClient         │
├─────────────────────┤
│ - provider          │
│ - api_key           │
├─────────────────────┤
│ + generate_text()   │
│ + analyze_vision()  │
└─────────────────────┘

┌─────────────────────┐
│  PortfolioService   │
├─────────────────────┤
│ - repository        │
│ - analyzer          │
│ - risk_analyzer     │
├─────────────────────┤
│ + analyze_portfolio()│
│ + get_rebalancing() │
└──────────┬──────────┘
           │
           │ uses
           ▼
┌─────────────────────┐
│ PortfolioAnalyzer   │
├─────────────────────┤
│ + analyze()         │
│ + calculate_allocation()│
│ + calculate_performance()│
└─────────────────────┘

┌─────────────────────┐
│  ScreenshotService   │
├─────────────────────┤
│ - repository        │
│ - llm_client        │
│ - image_processor   │
├─────────────────────┤
│ + upload()          │
│ + analyze()         │
│ + extract_data()   │
└─────────────────────┘
```

### 7.2 주요 클래스 상세

#### 7.2.1 InvestmentAgent

```python
class InvestmentAgent:
    """투자 상담 Agent"""
    
    def __init__(self, llm_provider: str, api_key: str):
        self.llm_client = LLMClient(provider=llm_provider, api_key=api_key)
        self.portfolio_service = PortfolioService()
        self.conversation_history = []
    
    async def chat(self, message: str, user_id: int) -> str:
        """사용자와 대화"""
        # 컨텍스트 수집
        context = await self._build_context(user_id)
        
        # LLM에 전달
        response = await self.llm_client.generate(
            messages=self.conversation_history + [
                {"role": "user", "content": message}
            ],
            context=context
        )
        
        # 대화 기록 업데이트
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    async def analyze_screenshot(self, image_path: str, user_id: int) -> Dict[str, Any]:
        """스크린샷 분석"""
        # Vision API로 이미지 분석
        extracted_data = await self.llm_client.analyze_vision(
            image_path=image_path,
            prompt="Extract portfolio information from this screenshot..."
        )
        
        # 포트폴리오 분석
        analysis = await self.portfolio_service.analyze_from_data(
            user_id=user_id,
            portfolio_data=extracted_data
        )
        
        return analysis
```

#### 7.2.2 PortfolioAnalyzer

```python
class PortfolioAnalyzer:
    """포트폴리오 분석기"""
    
    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
    
    async def analyze(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """종합 분석"""
        return {
            'allocation': self._calculate_allocation(portfolio),
            'performance': await self.performance_analyzer.analyze(portfolio),
            'risk': await self.risk_analyzer.assess(portfolio),
            'diversification': self._calculate_diversification(portfolio)
        }
    
    def _calculate_allocation(self, portfolio: Dict) -> Dict[str, float]:
        """자산 배분 계산"""
        total = sum(asset['value'] for asset in portfolio['assets'])
        return {
            asset['type']: asset['value'] / total * 100
            for asset in portfolio['assets']
        }
```

---

## 8. 데이터 흐름

### 8.1 스크린샷 분석 플로우

```
사용자 업로드
    │
    ▼
[이미지 검증]
    │
    ▼
[이미지 저장 (암호화)]
    │
    ▼
[LLM Vision API 호출]
    │
    ▼
[정보 추출]
    │
    ▼
[사용자 확인]
    │
    ▼
[포트폴리오 분석]
    │
    ▼
[Agent 평가]
    │
    ▼
[결과 저장]
    │
    ▼
[사용자에게 표시]
```

### 8.2 추천 생성 플로우

```
사용자 요청
    │
    ▼
[재무 상황 조회]
    │
    ▼
[투자 성향 조회]
    │
    ▼
[목표 조회]
    │
    ▼
[포트폴리오 최적화]
    │
    ▼
[리스크 평가]
    │
    ▼
[Agent 근거 생성]
    │
    ▼
[추천 저장]
    │
    ▼
[사용자에게 표시]
```

### 8.3 Agent 대화 플로우

```
사용자 메시지
    │
    ▼
[컨텍스트 수집]
  - 포트폴리오 정보
  - 투자 성향
  - 최근 거래
    │
    ▼
[LLM API 호출]
    │
    ▼
[응답 생성]
    │
    ▼
[근거 추가]
    │
    ▼
[사용자에게 표시]
```

---

## 9. 보안 설계

### 9.1 인증 및 인가

- **비밀번호 해싱**: bcrypt 사용 (salt rounds: 12)
- **세션 관리**: Streamlit Session State + JWT 토큰 (향후)
- **API 키 관리**: 환경 변수 + 암호화된 설정 파일

### 9.2 데이터 보안

- **데이터베이스 암호화**: 민감 정보 필드 암호화
- **이미지 저장**: 암호화된 스토리지
- **전송 보안**: HTTPS 필수

### 9.3 입력 검증

- **SQL Injection 방지**: ORM 사용, 파라미터화된 쿼리
- **XSS 방지**: 입력 데이터 sanitization
- **파일 업로드 검증**: 파일 타입, 크기 제한

### 9.4 접근 제어

- **사용자별 데이터 격리**: user_id 기반 필터링
- **권한 관리**: 역할 기반 접근 제어 (향후)

---

## 10. 성능 최적화

### 10.1 캐싱 전략

- **Redis 캐싱**:
  - 포트폴리오 분석 결과 (TTL: 1시간)
  - 시장 데이터 (TTL: 5분)
  - 사용자 프로필 (TTL: 30분)

### 10.2 비동기 처리

- **비동기 I/O**: asyncio, aiohttp 사용
- **백그라운드 작업**: 이미지 분석, 리포트 생성

### 10.3 데이터베이스 최적화

- **인덱싱**: user_id, created_at 등 주요 필드
- **쿼리 최적화**: N+1 문제 방지, 배치 조회

### 10.4 LLM API 최적화

- **요청 배칭**: 여러 요청을 배치로 처리
- **응답 캐싱**: 유사한 질문에 대한 응답 캐싱
- **Rate Limiting**: API 호출 제한 관리

---

## 11. 배포 구조

### 11.1 개발 환경

```
개발자 로컬
    │
    ▼
[WSL 환경]
    │
    ▼
[Python 가상환경]
    │
    ▼
[Streamlit 앱]
    │
    ▼
[로컬 PostgreSQL]
```

### 11.2 프로덕션 환경 (향후)

```
사용자
    │
    ▼
[CDN / Load Balancer]
    │
    ▼
[Web Server (Nginx)]
    │
    ▼
[Application Server]
  - Streamlit App
  - FastAPI (REST API)
    │
    ▼
[Database]
  - PostgreSQL (Primary)
  - Redis (Cache)
    │
    ▼
[External Services]
  - LLM APIs
  - Financial Data APIs
```

### 11.3 Docker 구성 (향후)

```dockerfile
# Dockerfile 예시
FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install uv && uv sync

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 12. 테스트 전략

### 12.1 단위 테스트

- **범위**: Service, Analyzer, Optimizer 모듈
- **도구**: pytest
- **목표 커버리지**: 80% 이상

### 12.2 통합 테스트

- **범위**: API 엔드포인트, 데이터베이스 연동
- **도구**: pytest + pytest-asyncio
- **테스트 DB**: 별도 테스트 데이터베이스

### 12.3 E2E 테스트

- **범위**: 주요 사용자 시나리오
- **도구**: Playwright (Streamlit UI 테스트)

---

## 13. 모니터링 및 로깅

### 13.1 로깅

- **레벨**: DEBUG, INFO, WARNING, ERROR
- **형식**: JSON (구조화된 로그)
- **저장**: 파일 + 외부 로깅 서비스 (향후)

### 13.2 모니터링

- **성능 지표**: 응답 시간, 처리량
- **에러 추적**: 에러 발생률, 스택 트레이스
- **비즈니스 지표**: 사용자 수, 추천 생성 수

---

## 14. 향후 확장 계획

### 14.1 자동 구매 기능

- 증권사 API 연동
- 자동 주문 실행
- 리밸런싱 자동화

### 14.2 모바일 앱

- React Native 기반 모바일 앱
- 푸시 알림

### 14.3 고급 기능

- 머신러닝 기반 시장 예측
- 소셜 투자 기능
- 블록체인 기반 투명성

---

## 15. 개발 일정 (예시)

### Phase 1 (기본 기능)
- 사용자 관리 및 인증
- LLM Agent 기본 구조
- 투자 성향 관리
- 기본 자산 배분 추천

### Phase 2 (핵심 기능)
- 포트폴리오 분석
- 스크린샷 분석
- 리스크 관리
- 성과 분석

### Phase 3 (고급 기능)
- 리밸런싱 자동화
- 목표 기반 계획
- 트랜드 분석
- 자동 구매 준비

---

## 16. 참고 자료

- Modern Portfolio Theory (MPT)
- Black-Litterman Model
- Value at Risk (VaR) 계산
- Sharpe Ratio, Information Ratio
- 금융투자업법 관련 규정

---

## 17. Python 전문가 검토 의견

### 17.1 개선이 필요한 사항

#### ⚠️ 1. 타입 힌팅 및 타입 안정성

**현재 문제점:**
- `Dict[str, Any]` 과도한 사용으로 타입 안정성 저하
- 반환 타입이 구체적이지 않음
- Optional 타입 명시 부족

**개선 방안:**
```python
# 개선 전
async def analyze_portfolio(self, user_id: int) -> Dict[str, Any]:
    pass

# 개선 후
from typing import TypedDict, Optional
from dataclasses import dataclass

@dataclass
class PortfolioAnalysis:
    total_value: float
    asset_allocation: Dict[str, float]
    diversification_score: float
    performance: PerformanceMetrics

async def analyze_portfolio(self, user_id: int) -> PortfolioAnalysis:
    pass
```

**추가 필요:**
- `TypedDict` 사용으로 딕셔너리 구조 명확화
- `dataclasses` 또는 `pydantic` 모델 사용
- `mypy` 타입 체킹 도입

#### ⚠️ 2. 의존성 주입 (Dependency Injection)

**현재 문제점:**
- Service 클래스에서 직접 의존성 생성 (`self.repository = PortfolioRepository()`)
- 테스트 어려움
- 결합도 높음

**개선 방안:**
```python
# 개선 전
class PortfolioService:
    def __init__(self):
        self.repository = PortfolioRepository()
        self.analyzer = PortfolioAnalyzer()

# 개선 후
class PortfolioService:
    def __init__(
        self,
        repository: PortfolioRepository,
        analyzer: PortfolioAnalyzer,
        risk_analyzer: RiskAnalyzer
    ):
        self.repository = repository
        self.analyzer = analyzer
        self.risk_analyzer = risk_analyzer
```

**추가 필요:**
- 의존성 주입 컨테이너 도입 (예: `dependency-injector`)
- Factory 패턴 활용

#### ⚠️ 3. 에러 처리 전략

**현재 문제점:**
- 에러 처리 전략이 명시되지 않음
- 커스텀 예외 클래스 부재
- 에러 핸들링 일관성 부족

**개선 방안:**
```python
# 커스텀 예외 정의
class BUJAException(Exception):
    """기본 예외 클래스"""
    pass

class UserNotFoundError(BUJAException):
    """사용자를 찾을 수 없음"""
    pass

class PortfolioAnalysisError(BUJAException):
    """포트폴리오 분석 오류"""
    pass

class LLMAPIError(BUJAException):
    """LLM API 호출 오류"""
    pass

# 에러 핸들링
async def analyze_portfolio(self, user_id: int) -> PortfolioAnalysis:
    try:
        portfolio = await self.repository.get_user_portfolio(user_id)
        if not portfolio:
            raise UserNotFoundError(f"User {user_id} not found")
        return await self.analyzer.analyze(portfolio)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise PortfolioAnalysisError("Failed to analyze portfolio") from e
```

#### ⚠️ 4. Streamlit과 비동기 처리 통합

**현재 문제점:**
- Streamlit은 기본적으로 동기식
- 비동기 함수 호출 방법 불명확
- 세션 관리와 비동기 처리 통합 방법 부재

**개선 방안:**
```python
# Streamlit에서 비동기 함수 호출
import asyncio
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

def run_async(coro):
    """Streamlit에서 비동기 함수 실행"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# 사용 예시
async def get_portfolio_analysis(user_id: int):
    service = PortfolioService(...)
    return await service.analyze_portfolio(user_id)

# Streamlit 페이지에서
if st.button("분석하기"):
    result = run_async(get_portfolio_analysis(user_id))
    st.write(result)
```

**추가 필요:**
- `asyncio.run()` vs `loop.run_until_complete()` 선택 기준
- Streamlit 세션별 이벤트 루프 관리

#### ⚠️ 5. 환경 변수 및 설정 관리

**현재 문제점:**
- 설정 관리 전략이 구체적이지 않음
- 환경별 설정 분리 방법 부재

**개선 방안:**
```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    database_pool_size: int = 10
    
    # LLM
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: str = "openai"
    
    # Redis
    redis_url: Optional[str] = None
    redis_ttl: int = 3600
    
    # Security
    secret_key: str
    bcrypt_rounds: int = 12
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
```

**추가 필요:**
- `pydantic-settings` 사용
- 환경별 설정 파일 분리 (dev, prod, test)

#### ⚠️ 6. 로깅 전략 구체화

**현재 문제점:**
- 로깅 전략이 추상적
- 구조화된 로깅 방법 부재

**개선 방안:**
```python
# config/logging.py
import logging
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """JSON 형식 로거"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 추가 컨텍스트
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        return json.dumps(log_data)

def setup_logging(level: str = "INFO"):
    """로깅 설정"""
    logger = logging.getLogger("buja")
    logger.setLevel(getattr(logging, level))
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger
```

#### ⚠️ 7. 데이터 검증 전략

**현재 문제점:**
- 입력 데이터 검증 방법 불명확
- Pydantic 모델 활용 부족

**개선 방안:**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal

class InvestmentRecordCreate(BaseModel):
    """투자 기록 생성 모델"""
    asset_type: str = Field(..., regex="^(STOCK|BOND|FUND|CRYPTO)$")
    symbol: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    buy_price: Decimal = Field(..., gt=0)
    buy_date: date
    
    @validator('symbol')
    def validate_symbol(cls, v, values):
        if values.get('asset_type') in ['STOCK', 'BOND'] and not v:
            raise ValueError("Symbol is required for STOCK and BOND")
        return v

class PortfolioService:
    async def create_investment_record(
        self, 
        user_id: int, 
        record_data: InvestmentRecordCreate
    ) -> InvestmentRecord:
        # Pydantic이 자동으로 검증
        return await self.repository.create(record_data)
```

#### ⚠️ 8. 캐싱 구현 세부사항

**현재 문제점:**
- 캐싱 전략이 추상적
- 캐시 키 생성 방법 불명확
- 캐시 무효화 전략 부재

**개선 방안:**
```python
from functools import wraps
from typing import Callable, Any
import hashlib
import json
import redis.asyncio as redis

class CacheManager:
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 3600):
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def cached(self, prefix: str, ttl: int = None):
        """캐싱 데코레이터"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = self.cache_key(prefix, *args, **kwargs)
                
                # 캐시에서 조회
                cached = await self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
                
                # 실행 및 캐싱
                result = await func(*args, **kwargs)
                await self.redis.setex(
                    cache_key,
                    ttl or self.default_ttl,
                    json.dumps(result, default=str)
                )
                return result
            return wrapper
        return decorator

# 사용 예시
cache_manager = CacheManager(redis_client)

class PortfolioService:
    @cache_manager.cached("portfolio:analysis", ttl=3600)
    async def analyze_portfolio(self, user_id: int) -> PortfolioAnalysis:
        # 분석 로직
        pass
```

#### ⚠️ 9. 데이터베이스 세션 관리

**현재 문제점:**
- SQLAlchemy 세션 관리 방법 불명확
- 비동기 세션 사용 여부 불명확
- 트랜잭션 관리 전략 부재

**개선 방안:**
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager

class Database:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def session(self):
        """세션 컨텍스트 매니저"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

# Repository에서 사용
class PortfolioRepository:
    def __init__(self, db: Database):
        self.db = db
    
    async def get_user_portfolio(self, user_id: int):
        async with self.db.session() as session:
            result = await session.execute(
                select(Portfolio).where(Portfolio.user_id == user_id)
            )
            return result.scalar_one_or_none()
```

#### ⚠️ 10. 테스트 가능성 개선

**현재 문제점:**
- Mock 객체 사용 방법 불명확
- 테스트 픽스처 전략 부재

**개선 방안:**
```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.portfolio_service import PortfolioService
from src.repositories.portfolio_repository import PortfolioRepository

@pytest.fixture
def mock_repository():
    """Mock Repository"""
    repo = MagicMock(spec=PortfolioRepository)
    repo.get_user_portfolio = AsyncMock(return_value={"assets": []})
    return repo

@pytest.fixture
def portfolio_service(mock_repository):
    """PortfolioService with mocked dependencies"""
    return PortfolioService(
        repository=mock_repository,
        analyzer=MagicMock(),
        risk_analyzer=MagicMock()
    )

# 테스트
@pytest.mark.asyncio
async def test_analyze_portfolio(portfolio_service, mock_repository):
    result = await portfolio_service.analyze_portfolio(user_id=1)
    assert result is not None
    mock_repository.get_user_portfolio.assert_called_once_with(1)
```

### 17.2 추가 권장 사항

#### ✅ 1. 프로젝트 구조 개선

```
BUJA/
├── src/
│   ├── domain/              # 도메인 모델 (추가)
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   └── investment.py
│   ├── infrastructure/       # 인프라 계층 (추가)
│   │   ├── database/
│   │   ├── cache/
│   │   └── storage/
│   └── ...
```

#### ✅ 2. 의존성 추가 (pyproject.toml)

```toml
dependencies = [
    "streamlit>=1.28.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "Pillow>=10.0.0",
    # 추가 필요
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",  # PostgreSQL async driver
    "alembic>=1.13.0",
    "redis>=5.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "openai>=1.0.0",
    "anthropic>=0.18.0",
    "httpx>=0.25.0",
    "bcrypt>=4.1.0",
    "python-dotenv>=1.0.0",
    "scipy>=1.11.0",  # 최적화 알고리즘
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.12.0",
    "mypy>=1.7.0",
    "black>=23.11.0",
    "ruff>=0.1.6",
    "pytest-cov>=4.1.0",
]
```

#### ✅ 3. 코드 품질 도구

- **mypy**: 타입 체킹
- **black**: 코드 포맷팅
- **ruff**: 린팅 (flake8 + isort 대체)
- **pytest-cov**: 테스트 커버리지

#### ✅ 4. 비동기 처리 최적화

- `asyncio.gather()` 사용으로 병렬 처리
- `asyncio.Semaphore`로 동시성 제어
- 백그라운드 작업은 `asyncio.create_task()` 활용

#### ✅ 5. 메모리 관리

- 대용량 데이터 처리 시 청크 단위 처리
- 이미지 처리 후 즉시 메모리 해제
- Generator 패턴 활용

### 17.3 긍정적인 부분

✅ **좋은 점:**
1. 계층 구조가 명확함 (Presentation, Application, Business Logic, Data Access)
2. Repository 패턴 적용
3. 비동기 처리 고려
4. 모듈화된 구조
5. 확장 가능한 아키텍처

### 17.4 우선순위별 개선 사항

**높은 우선순위:**
1. 타입 힌팅 및 Pydantic 모델 도입
2. 의존성 주입 패턴 적용
3. 에러 처리 전략 수립
4. Streamlit-비동기 통합 방법 명확화

**중간 우선순위:**
5. 환경 변수 및 설정 관리 구체화
6. 로깅 전략 구현
7. 데이터 검증 전략
8. 데이터베이스 세션 관리

**낮은 우선순위:**
9. 캐싱 구현 세부사항
10. 테스트 전략 보완

---

**문서 버전**: 1.1  
**최종 수정일**: 2024  
**작성자**: BUJA 개발팀  
**검토자**: Python 전문가

