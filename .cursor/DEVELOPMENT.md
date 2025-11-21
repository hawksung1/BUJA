# BUJA Development Guide

> Coding standards and best practices

## Code Style

### Python Standards
- **PEP 8** compliance
- **Type hints** for function signatures
- **Docstrings** for public APIs (Google style)

### Naming Conventions
```python
# Classes: PascalCase
class InvestmentAgent:
    pass

# Functions/variables: snake_case
def calculate_portfolio_value():
    user_id = 1

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# Private: _leading_underscore
def _internal_helper():
    pass
```

### Import Order
```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
import streamlit as st
import pandas as pd

# 3. Local
from src.models.user import User
from src.services.user_service import UserService
```

### Comments
- **Korean** for user-facing strings and complex logic explanations
- **English** for code comments and docstrings
- Keep comments concise and meaningful

## Testing

### Test Structure
```
tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
├── e2e/               # End-to-end (Playwright)
└── fixtures/          # Test data
```

### Writing Tests
```python
import pytest
from src.services.portfolio_service import PortfolioService

class TestPortfolioService:
    def test_calculate_value(self):
        """Test portfolio value calculation"""
        service = PortfolioService()
        portfolio = create_test_portfolio()
        
        value = service.calculate_value(portfolio)
        
        assert value > 0
        assert isinstance(value, float)
```

### Running Tests
```bash
uv run pytest              # All tests
uv run pytest tests/unit/  # Unit only
uv run pytest -v           # Verbose
uv run pytest --cov=src    # With coverage
```

### E2E Tests (Playwright)
```python
from playwright.sync_api import Page, expect

def test_login_flow(page: Page):
    """Test user login"""
    page.goto("http://localhost:8501")
    page.click("text=로그인")
    page.fill("input[name='username']", "test_user")
    page.fill("input[name='password']", "test_pass")
    page.click("button:has-text('로그인')")
    
    expect(page.locator("text=환영합니다")).to_be_visible()
```

## Commit Guidelines

### Format
```
<type>: <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no logic change)
- `refactor`: Code restructuring
- `test`: Test changes
- `chore`: Build/config changes

### Example
```
feat: Add risk tolerance assessment

- Implement questionnaire-based risk scoring
- Store results in user profile
- Update recommendation engine

Closes #123
```

## Debugging

### Logging
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Streamlit Debug
```python
import streamlit as st

if st.sidebar.checkbox("Debug Mode"):
    st.write("Debug info:", debug_data)
```

## Common Issues

### LLM API Errors
- Check API keys in `.env`
- Verify rate limits
- Check network connectivity

### Database Errors
- Verify connection string
- Check migrations status
- Ensure proper permissions

### Dependency Issues
```bash
uv sync                          # Reinstall all
uv pip install --force-reinstall package_name
```

## Code Review Checklist

### Required
- [ ] Tests written/updated
- [ ] Type hints added
- [ ] Docstrings for public APIs
- [ ] Error handling implemented
- [ ] Logging added (where appropriate)
- [ ] No hardcoded secrets
- [ ] Guides updated (if structure changed)

### Quality
- [ ] PEP 8 compliant
- [ ] No code duplication
- [ ] Functions are focused and small
- [ ] Clear naming

## Architecture Guidelines

### Service Layer
- Business logic only
- No direct database access (use repositories)
- Handle transactions
- Return domain objects

### Repository Layer
- Database operations only
- CRUD methods
- Query optimization
- Return models

### Agent Layer
- LLM interaction
- Tool integration
- Context management
- Streaming support

### Middleware
- Authentication
- Error handling
- Logging
- Request validation

## Performance

### Database
- Use async where possible
- Batch operations
- Proper indexing
- Connection pooling

### LLM Calls
- Async/await for non-blocking
- Streaming for better UX
- Caching where appropriate
- Timeout handling

### Streamlit
- Use `@st.cache_data` for expensive operations
- Minimize reruns
- Lazy loading for large datasets

## Security

### API Keys
- Never commit `.env` files
- Use environment variables
- Rotate keys regularly

### User Data
- Hash passwords (bcrypt)
- Validate all inputs
- Sanitize user content
- Proper session management

### Database
- Parameterized queries (SQLAlchemy handles this)
- Principle of least privilege
- Regular backups

## References

- Architecture: `.cursor/ARCHITECTURE.md`
- Project guide: `.cursor/CURSOR_GUIDE.md`
- Requirements: `docs/REQUIREMENTS.md`
- Design: `docs/DESIGN.md`
