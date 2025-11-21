# BUJA - Cursor Guide

> Quick reference for AI-assisted development

## Project Overview

**BUJA**: LLM-based asset management & investment advisor
- **Stack**: Python 3.10+, Streamlit, uv, SQLAlchemy, PostgreSQL
- **Features**: AI chat, portfolio analysis, risk assessment, investment recommendations

## Quick Reference

### Essential Files
| Path | Purpose |
|------|---------|
| `.cursor/ARCHITECTURE.md` | System design |
| `.cursor/DEVELOPMENT.md` | Dev rules |
| `docs/REQUIREMENTS.md` | Requirements (503 lines - **reference only**) |
| `docs/DESIGN.md` | Detailed design (1719 lines - **reference only**) |
| `app.py` | Streamlit entry point |
| `src/` | Source code modules |
| `pages/` | Streamlit pages |
| `tests/` | Test suites |

### Commands
```bash
uv run streamlit run app.py  # Dev server
uv sync                      # Install deps
uv run pytest                # Run tests
```

## Workflow

### Before Starting
1. Check `.cursor/rules`
2. Review relevant guide (ARCHITECTURE or DEVELOPMENT)
3. Understand scope

### During Development
1. **Minimal context**: Read only necessary files
2. **Large files**: Reference specific sections only
3. **Tests required**: Update/create tests for changes
4. **Korean responses**: User-facing text in Korean

### After Completion
1. Run tests
2. Check linter
3. Update guides if structure changed

## Structure Overview

```
BUJA/
├── app.py                  # Main entry
├── pages/                  # UI pages (8 files)
│   ├── login.py
│   ├── dashboard.py
│   ├── agent_chat.py
│   └── ...
├── src/                    # Source code
│   ├── agents/             # LLM agents
│   ├── analyzers/          # Portfolio/risk analysis
│   ├── services/           # Business logic
│   ├── repositories/       # Data access
│   ├── models/             # SQLAlchemy models
│   └── utils/              # Helpers
├── tests/                  # Tests (unit/integration/e2e)
├── config/                 # Configuration
└── docs/                   # Documentation
```

## Key Principles

1. **Layer separation**: Presentation → Service → Repository → Model
2. **Test coverage**: All changes must have tests
3. **Type hints**: Use where applicable
4. **Async support**: For LLM and I/O operations
5. **Error handling**: Proper exception handling and logging

## Common Tasks

### Add New Feature
1. Check requirements in `docs/REQUIREMENTS.md`
2. Review architecture in `.cursor/ARCHITECTURE.md`
3. Implement in appropriate layer (service/repository/model)
4. Add tests
5. Update UI if needed

### Fix Bug
1. Locate issue (check logs, tests)
2. Write failing test
3. Fix code
4. Verify test passes
5. Check for regressions

### Add New Page
1. Create file in `pages/`
2. Follow auth pattern from existing pages
3. Add e2e test in `tests/e2e/`
4. Update navigation if needed

## Troubleshooting

### App won't start
→ Check `README.md` setup section

### Dependency issues
→ Run `uv sync`

### Test failures
→ Check `pytest.ini`, run with `-v` flag

### LLM API errors
→ Verify API keys in `.env`

## Notes

- **Large docs**: `REQUIREMENTS.md` (503 lines), `DESIGN.md` (1719 lines) - reference sections only
- **Context optimization**: Only load files you need
- **Guide updates**: Update `.cursor/` files when structure changes
