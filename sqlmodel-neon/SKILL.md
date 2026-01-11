---
name: sqlmodel-neon
description: FastAPI + Neon PostgreSQL + SQLModel integration using UV package manager. Use when creating new FastAPI projects with Neon database, integrating Neon/SQLModel into existing FastAPI apps, setting up database connections, defining models with relationships, creating migrations with Alembic, or writing advanced queries. Includes full project template with async database sessions, CRUD operations, relationship loading, and production-ready configuration.
---

# FastAPI + Neon + SQLModel

Complete toolkit for building FastAPI applications with Neon PostgreSQL and SQLModel using UV package manager.

## Quick Start

### Create New Project

```bash
cd skills/sqlmodel-neon
python scripts/scaffold.py new my-project
cd my-project
```

Then set up your Neon connection in `.env`:

```bash
# Get connection string from https://console.neon.tech/
NEON_DATABASE_URL=postgresql+psycopg://user:password@host/database
```

Install and run:

```bash
uv sync
uv run uvicorn main:app --reload
```

### Add to Existing Project

```bash
cd skills/sqlmodel-neon
python scripts/scaffold.py add
```

This adds `database.py`, updates dependencies, and configures environment variables.

## Project Structure

The template includes:

```
fastapi-template/
├── pyproject.toml       # UV dependencies
├── database.py          # Async/sync database sessions
├── main.py              # Complete FastAPI app with CRUD
├── .env.example         # Neon connection template
└── .gitignore
```

## Database Configuration

`database.py` provides both sync and async database sessions:

```python
from database import get_async_session, settings

# Settings load from environment
settings.neon_database_url  # Your Neon connection string
settings.resolved_async_url # Auto-converted async URL

# Dependency injection in FastAPI
@app.get("/users/")
async def list_users(session=Depends(get_async_session)):
    result = await session.execute(select(User))
    return result.scalars().all()
```

## Defining Models

SQLModel combines Pydantic and SQLAlchemy:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    posts: List["Post"] = Relationship(back_populates="author")


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str | None = None
    user_id: int = Field(foreign_key="user.id")
    author: User | None = Relationship(back_populates="posts")
```

## CRUD Operations

### Create

```python
@app.post("/users/")
async def create_user(user: UserCreate, session=Depends(get_async_session)):
    db_user = User.model_validate(user)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
```

### Read

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int, session=Depends(get_async_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user
```

### Update

```python
@app.patch("/users/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate, session=Depends(get_async_session)):
    user = await session.get(User, user_id)
    user_data = user_update.model_dump(exclude_unset=True)
    for field, value in user_data.items():
        setattr(user, field, value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

### Delete

```python
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, session=Depends(get_async_session)):
    user = await session.get(User, user_id)
    await session.delete(user)
    await session.commit()
```

## Reference Documentation

For advanced patterns, see these references:

- **[Migrations with Alembic](references/migrations.md)** - Database migrations, branching with Neon
- **[Relationships](references/relationships.md)** - One-to-many, many-to-many, self-referential
- **[Advanced Queries](references/queries.md)** - Filtering, joins, aggregations, batch operations

## Neon Database Setup

1. Go to [console.neon.tech](https://console.neon.tech/)
2. Create a free account
3. Create a new project
4. Copy the connection string (choose "Psycopg" format)
5. Paste into `.env` file

## UV Package Manager

This skill uses UV for fast dependency management:

```bash
# Install dependencies
uv sync

# Run application
uv run uvicorn main:app --reload

# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name
```

## Async vs Sync

The template supports both patterns:

**Async (recommended for FastAPI):**
```python
from database import get_async_session

@app.get("/users/")
async def list_users(session=Depends(get_async_session)):
    result = await session.execute(select(User))
    return result.scalars().all()
```

**Sync (for scripts/migrations):**
```python
from database import get_session, sync_engine

def list_users_sync():
    with Session(sync_engine) as session:
        result = session.exec(select(User))
        return result.all()
```

## Common Patterns

### Pagination

```python
@app.get("/users/")
async def list_users(
    offset: int = 0,
    limit: int = 100,
    session=Depends(get_async_session)
):
    result = await session.execute(
        select(User).offset(offset).limit(limit)
    )
    return result.scalars().all()
```

### Search

```python
from sqlmodel import col

@app.get("/users/search/")
async def search_users(q: str, session=Depends(get_async_session)):
    result = await session.execute(
        select(User).where(col(User.email).icontains(q))
    )
    return result.scalars().all()
```

### Count

```python
from sqlalchemy import func

@app.get("/users/count")
async def count_users(session=Depends(get_async_session)):
    result = await session.execute(
        select(func.count()).select_from(User)
    )
    return {"count": result.scalar()}
```

## Environment Variables

Required in `.env`:

```bash
# Neon PostgreSQL Connection String
NEON_DATABASE_URL=postgresql+psycopg://user:password@host/database
```

Optional for async override:

```bash
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@host/database
```
