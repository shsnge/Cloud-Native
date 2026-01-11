"""
Database configuration and session management for Neon PostgreSQL + SQLModel.
"""
import os
from typing import AsyncGenerator

from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Neon PostgreSQL Connection String
    # Format: postgresql+psycopg://user:password@host/database
    neon_database_url: str = "sqlite:///./test.db"

    # Async connection string (with +asyncpg)
    async_database_url: str | None = None

    @property
    def resolved_async_url(self) -> str:
        """Get async database URL, converting sync URL if needed."""
        if self.async_database_url:
            return self.async_database_url
        # Convert postgresql:// to postgresql+asyncpg://
        return self.neon_database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        ).replace(
            "postgresql+psycopg://", "postgresql+asyncpg://"
        )


settings = Settings()

# Sync engine for simple operations
sync_engine = create_engine(settings.neon_database_url, echo=False)

# Async engine for better performance
async_engine = create_async_engine(
    settings.resolved_async_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_session() -> Generator[Session, None, None]:
    """Get a synchronous database session (for simple scripts)."""
    with Session(sync_engine) as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session (for FastAPI dependency injection)."""
    async with async_session_maker() as session:
        yield session


def init_db() -> None:
    """Initialize database tables (synchronous)."""
    SQLModel.metadata.create_all(sync_engine)


async def init_async_db() -> None:
    """Initialize database tables (asynchronous)."""
    from sqlmodel.ext.asyncio.session import AsyncSession
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
