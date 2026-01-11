# Database Migrations with Alembic

This guide covers database migrations using Alembic with SQLModel and Neon PostgreSQL.

## Setup Alembic

Add Alembic to your `pyproject.toml`:

```toml
[tool.uv]
dev-dependencies = [
    "alembic>=1.13.0",
]
```

Then initialize Alembic:

```bash
uv sync
uv run alembic init alembic
```

## Configure Alembic

Edit `alembic/env.py` to import your models and use SQLAlchemy async:

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your Base and models
from sqlmodel import SQLModel
from database import settings
from main import User, Post  # Import all your models

# this is the Alembic Config object
config = context.config

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.resolved_async_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Creating Migrations

### Auto-generate from models

```bash
# Generate migration based on model changes
uv run alembic revision --autogenerate -m "Add user table"
```

### Manual migration

```bash
# Create empty migration
uv run alembic revision -m "Custom migration"
```

Then edit the generated migration file:

```python
"""Add user table

Revision ID: 001
Revises:
Create Date: 2024-01-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration."""
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)


def downgrade() -> None:
    """Rollback migration."""
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
```

## Running Migrations

```bash
# Upgrade to latest
uv run alembic upgrade head

# Upgrade to specific version
uv run alembic upgrade 001

# Downgrade one step
uv run alembic downgrade -1

# Downgrade to base (remove all)
uv run alembic downgrade base

# View migration history
uv run alembic history

# View current version
uv run alembic current
```

## Migration Best Practices

1. **Always review auto-generated migrations** - Auto-generate is helpful but not perfect
2. **Keep migrations reversible** - Write both `upgrade()` and `downgrade()`
3. **Don't modify committed migrations** - Create a new one instead
4. **Test migrations in development first** - Neon allows easy branch databases
5. **Use transactions** - Alembic wraps migrations in transactions by default

## Neon-Specific Workflow

Neon makes migrations safer with database branching:

```bash
# Create a branch for testing migrations
# (via Neon CLI or console)
neon branches create test-migration

# Set your database URL to the branch
# Run migrations
uv run alembic upgrade head

# Test your application

# If good, apply to main database
# If bad, delete the branch and try again
```
