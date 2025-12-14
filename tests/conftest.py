"""Pytest configuration and fixtures."""

import os
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import Settings, get_settings, reset_settings
from src.internal.model.entity.base import Base
from src.internal.store.database import (
    DatabaseManager,
    get_database_manager,
    reset_database_manager,
)


@pytest.fixture(scope="function")
def test_settings() -> Settings:
    """Create test settings with test database configuration."""
    # Reset settings to ensure clean state
    reset_settings()

    # Override with test database settings
    os.environ.setdefault("DB_HOST", "localhost")
    os.environ.setdefault("DB_PORT", "5432")
    os.environ.setdefault("DB_NAME", "gmaps_scraper_test")
    os.environ.setdefault("DB_USER", "test_user")
    os.environ.setdefault("DB_PASSWORD", "test_password")
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("DEBUG", "false")

    settings = get_settings()
    yield settings

    # Cleanup
    reset_settings()
    # Clear environment variables
    for key in list(os.environ.keys()):
        if key.startswith("DB_") or key in ["ENVIRONMENT", "DEBUG"]:
            os.environ.pop(key, None)


@pytest.fixture(scope="function")
def test_db_manager(test_settings: Settings) -> DatabaseManager:
    """Create test database manager."""
    reset_database_manager()
    manager = get_database_manager()
    yield manager
    # Cleanup will be handled by disconnect in tests


@pytest.fixture(scope="function")
async def test_db_session(
    test_db_manager: DatabaseManager,
) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Use in-memory SQLite for unit tests (faster, no setup required)
    # For integration tests, use actual PostgreSQL
    async with test_db_manager.get_session() as session:
        yield session


@pytest.fixture(scope="function")
async def async_test_db() -> AsyncGenerator[None, None]:
    """Setup and teardown test database."""
    # This fixture can be used for integration tests that need a real database
    # For now, we'll use it to ensure proper cleanup
    yield
    # Cleanup handled by test_db_manager fixture


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singletons before each test to ensure isolation."""
    reset_settings()
    reset_database_manager()
    yield
    reset_settings()
    reset_database_manager()
