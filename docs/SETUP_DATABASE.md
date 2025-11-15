# Database Setup Guide

## Quick Setup

### Option 1: Using Docker (Recommended)

1. Start PostgreSQL container:
```bash
docker compose -f docker-compose.local.yml up -d postgres
```

2. Wait for database to be ready (about 10 seconds)

3. Create initial migration:
```bash
# If using uv
uv run alembic revision --autogenerate -m "Initial migration"

# Or directly
alembic revision --autogenerate -m "Initial migration"
```

4. Apply migration:
```bash
uv run alembic upgrade head
# Or
alembic upgrade head
```

### Option 2: Using Local PostgreSQL

1. Install PostgreSQL locally

2. Create database:
```sql
CREATE DATABASE buja_local;
```

3. Update `.env.local`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/buja_local
```

4. Create and apply migration (same as Option 1)

## Verify Setup

After setup, you should be able to:
- Register a new user
- Login
- Set investment preferences
- Chat with the agent (if LLM API key is set)

## Troubleshooting

### Database Connection Error
- Check if PostgreSQL is running
- Verify DATABASE_URL in `.env.local`
- Check database credentials

### Migration Error
- Ensure database exists
- Check database user permissions
- Verify models are imported correctly

