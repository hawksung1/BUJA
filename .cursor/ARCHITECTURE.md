# BUJA Architecture

> Minimal architecture guide for efficient context usage

## System Layers

```
┌─────────────────────────────────────┐
│  Presentation (Streamlit)           │  app.py, pages/
├─────────────────────────────────────┤
│  Business Logic                     │  src/services/
├─────────────────────────────────────┤
│  Agents (LLM)                       │  src/agents/
├─────────────────────────────────────┤
│  Data Access                        │  src/repositories/
├─────────────────────────────────────┤
│  Database                           │  src/models/ (SQLAlchemy)
└─────────────────────────────────────┘
```

## Module Structure

### Current Implementation

```
src/
├── agents/                 # LLM interaction
│   ├── base_agent.py
│   ├── investment_agent.py
│   ├── autonomous_investment_agent.py
│   └── tools/
├── analyzers/              # Analysis engines
│   ├── asset_allocator.py
│   ├── performance_analyzer.py
│   ├── portfolio_analyzer.py
│   └── risk_analyzer.py
├── external/               # External APIs
│   └── llm_client.py
├── middleware/             # Cross-cutting
│   ├── auth_middleware.py
│   └── error_handler.py
├── models/                 # SQLAlchemy models
│   ├── user.py
│   ├── portfolio.py
│   ├── investment.py
│   ├── chat.py
│   ├── financial.py
│   └── notification.py
├── repositories/           # Data access layer
│   ├── base_repository.py
│   ├── user_repository.py
│   ├── portfolio_repository.py
│   ├── chat_repository.py
│   └── notification_repository.py
├── services/               # Business logic
│   ├── user_service.py
│   ├── portfolio_service.py
│   ├── recommendation_service.py
│   ├── notification_service.py
│   ├── email_notification_service.py
│   ├── portfolio_monitoring_service.py
│   ├── goal_tracking_service.py
│   └── scheduler_service.py
└── utils/                  # Helpers
    ├── async_helpers.py
    ├── db.py
    └── validators.py
```

### Pages (Streamlit UI)

```
pages/
├── login.py                # Authentication
├── register.py             # User registration
├── onboarding.py           # Initial setup
├── dashboard.py            # Main dashboard
├── agent_chat.py           # LLM chat interface
├── investment_preference.py # Risk profile
├── profile.py              # User settings
└── mcp_tools.py            # MCP integration
```

## Data Flow

### Investment Consultation
```
User Input → Investment Agent → Analysis → Recommendation → Display
```

### Portfolio Analysis
```
Portfolio Data → Analyzers → Risk/Performance Metrics → Dashboard
```

### Chat Interaction
```
User Message → Agent (LLM) → Context + Tools → Response → Chat History
```

## Key Components

### 1. Agents (`src/agents/`)
- LLM-based conversation
- Investment advice generation
- Tool integration (MCP)
- Autonomous monitoring and action

### 2. Analyzers (`src/analyzers/`)
- Asset allocation (MPT, Black-Litterman)
- Risk analysis (VaR, Sharpe ratio)
- Performance tracking
- Portfolio optimization

### 3. Services (`src/services/`)
- Business logic layer
- Orchestrates repositories and analyzers
- Transaction management
- Portfolio monitoring (background)
- Goal tracking
- Notification delivery (email, extensible)

### 4. Repositories (`src/repositories/`)
- Database abstraction
- CRUD operations
- Query optimization

## Design Principles

1. **Separation of Concerns**: Each layer has single responsibility
2. **Dependency Injection**: Services receive dependencies
3. **Repository Pattern**: Data access abstraction
4. **Async Support**: Non-blocking I/O for LLM calls

## Extension Points

### Add New LLM Provider
- Extend `src/external/llm_client.py`
- Implement provider-specific client

### Add New Analysis Method
- Create analyzer in `src/analyzers/`
- Register in `src/services/analysis_service.py`

### Add New Page
- Create file in `pages/`
- Follow existing auth pattern

## References

- Detailed design: `docs/DESIGN.md` (1719 lines)
- Requirements: `docs/REQUIREMENTS.md` (503 lines)
- Dev guide: `.cursor/DEVELOPMENT.md`
