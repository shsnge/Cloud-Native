"""
Database configuration for Neon PostgreSQL + SQLModel.
"""
from sqlmodel import SQLModel, create_engine, Session
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database connection string
    # Default: SQLite for local development
    # For Neon PostgreSQL: postgresql+psycopg://user:password@host/database
    neon_database_url: str = "sqlite:///./tasks.db"
   


settings = Settings()

# Create engine
engine = create_engine(settings.neon_database_url, echo=False)


def get_session():
    """Get database session for FastAPI."""
    with Session(engine) as session:
        yield session


def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)
