"""
Shared fixtures and pytest configuration.

This file contains fixtures available to all tests in this directory.
"""

import os
import tempfile
from pathlib import Path

import pytest


# ============================================================================
# Test Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "network: marks tests that require network")


# ============================================================================
# Fixtures - Temporary Resources
# ============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory path."""
    return tmp_path


@pytest.fixture
def temp_file(tmp_path):
    """Provide a temporary file path."""
    return tmp_path / "test_file.txt"


# ============================================================================
# Fixtures - Sample Data
# ============================================================================

@pytest.fixture
def sample_user():
    """Provide a sample user object."""
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "active": True
    }


@pytest.fixture
def sample_config():
    """Provide sample configuration."""
    return {
        "debug": True,
        "database_url": ":memory:",
        "log_level": "INFO"
    }


# ============================================================================
# Fixtures - Mock Objects
# ============================================================================

@pytest.fixture
def mock_logger():
    """Provide a mock logger."""
    import logging
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to set environment variables for a test."""
    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
    return _set_env


# ============================================================================
# Fixtures - Database (example)
# ============================================================================

@pytest.fixture(scope="function")
def db_session():
    """Provide a test database session.

    Replace with your actual database setup.
    """
    # Setup
    db = {"data": {}}  # Mock database

    yield db

    # Teardown
    db["data"].clear()


# ============================================================================
# Fixtures - HTTP Client (example)
# ============================================================================

@pytest.fixture
def test_client():
    """Provide a test HTTP client.

    Replace with your actual client setup (e.g., TestClient for FastAPI).
    """
    # Import and configure your actual test client
    # from myapp import app
    # from fastapi.testclient import TestClient
    # return TestClient(app)

    class MockClient:
        def get(self, url):
            return MockResponse(200, {"status": "ok"})

        def post(self, url, data):
            return MockResponse(201, {"created": True})

    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data

        def json(self):
            return self._json

    return MockClient()


# ============================================================================
# Fixtures - Time helpers
# ============================================================================

@pytest.fixture
def freeze_time(monkeypatch):
    """Freeze time for testing."""
    from datetime import datetime, timezone
    frozen = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    class MockDatetime:
        @classmethod
        def now(cls, tz=None):
            return frozen

        @classmethod
        def utcnow(cls):
            return frozen

    monkeypatch.setattr("datetime.datetime", MockDatetime)
    return frozen
