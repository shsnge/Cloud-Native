"""
Pytest configuration and fixtures for Task Management API tests.

This file provides test fixtures and utilities for testing the FastAPI application.
"""
from typing import Generator
from datetime import datetime
from fastapi.testclient import TestClient

import pytest
from sqlmodel import SQLModel, create_engine, Session

# Test database URL (using SQLite for tests)
# Using file::memory: with cache=shared to allow multiple connections to the same in-memory DB
TEST_DATABASE_URL = "sqlite:///file:test_db?mode=memory&cache=shared"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    # Import models first to register them with SQLModel.metadata
    from main import Task, TaskStatus, TaskPriority

    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    # Create tables in the test database
    SQLModel.metadata.create_all(engine)

    yield engine

    # Drop tables after test
    SQLModel.metadata.drop_all(engine)

    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def test_client(test_session):
    """Create a test client with database session override."""
    from main import app, get_session

    # Override the database dependency
    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    # Create test client (using synchronous client for synchronous app)
    client = TestClient(app)
    yield client

    # Clean up overrides
    app.dependency_overrides.clear()


# =============================================================================
# Helper Functions for Creating Test Data
# =============================================================================

def create_test_task(
    session: Session,
    title: str = "Test Task",
    description: str = None,
    status: str = "todo",
    priority: str = "medium",
    due_date: datetime = None,
    tags: str = None,
    assignee_email: str = None
):
    """Helper function to create a test task in the database."""
    from main import Task, TaskStatus, TaskPriority

    task = Task(
        title=title,
        description=description,
        status=status if isinstance(status, TaskStatus) else TaskStatus(status),
        priority=priority if isinstance(priority, TaskPriority) else TaskPriority(priority),
        due_date=due_date,
        tags=tags,
        assignee_email=assignee_email
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# Export helper function
pytest.create_test_task = create_test_task
