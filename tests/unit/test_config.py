"""Tests for configuration system."""

import os
from unittest.mock import patch

import pytest

from src.config import Settings, get_settings, reset_settings
from src.config.api_config import APIConfig
from src.config.database_config import DatabaseConfig
from src.config.redis_config import RedisConfig


class TestSettings:
    """Tests for main Settings class."""

    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        reset_settings()
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_reset_settings(self):
        """Test that reset_settings creates a new instance."""
        reset_settings()
        settings1 = get_settings()
        reset_settings()
        settings2 = get_settings()
        assert settings1 is not settings2

    def test_default_values(self):
        """Test default configuration values."""
        reset_settings()
        settings = get_settings()

        assert settings.app_name == "google-map-scraper"
        assert settings.app_version == "0.1.0"
        assert settings.environment == "development"
        assert settings.debug is False

    def test_load_from_environment(self):
        """Test loading configuration from environment variables."""
        reset_settings()
        os.environ["APP_NAME"] = "test-app"
        os.environ["ENVIRONMENT"] = "production"
        os.environ["DEBUG"] = "true"

        settings = get_settings()

        assert settings.app_name == "test-app"
        assert settings.environment == "production"
        assert settings.debug is True

        # Cleanup
        os.environ.pop("APP_NAME", None)
        os.environ.pop("ENVIRONMENT", None)
        os.environ.pop("DEBUG", None)
        reset_settings()

    def test_database_config_nested(self):
        """Test that database config is properly nested."""
        reset_settings()
        settings = get_settings()

        assert isinstance(settings.database, DatabaseConfig)
        assert settings.database.host == "localhost"
        assert settings.database.port == 5432

    def test_redis_config_nested(self):
        """Test that redis config is properly nested."""
        reset_settings()
        settings = get_settings()

        assert isinstance(settings.redis, RedisConfig)
        assert settings.redis.host == "localhost"
        assert settings.redis.port == 6379

    def test_api_config_nested(self):
        """Test that API config is properly nested."""
        reset_settings()
        settings = get_settings()

        assert isinstance(settings.api, APIConfig)
        assert settings.api.host == "0.0.0.0"
        assert settings.api.port == 8000


class TestDatabaseConfig:
    """Tests for DatabaseConfig."""

    def test_default_values(self):
        """Test DatabaseConfig default values."""
        config = DatabaseConfig()

        assert config.host == "localhost"
        assert config.port == 5432
        assert config.name == "gmaps_scraper"
        assert config.user == "user"
        assert config.password == "password"
        assert config.pool_size == 10
        assert config.max_overflow == 20

    def test_load_from_environment(self):
        """Test loading DatabaseConfig from environment variables."""
        os.environ["DB_HOST"] = "test-host"
        os.environ["DB_PORT"] = "5433"
        os.environ["DB_NAME"] = "test_db"

        config = DatabaseConfig()

        assert config.host == "test-host"
        assert config.port == 5433
        assert config.name == "test_db"

        # Cleanup
        os.environ.pop("DB_HOST", None)
        os.environ.pop("DB_PORT", None)
        os.environ.pop("DB_NAME", None)

    def test_database_url_property(self):
        """Test database_url property generation."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            name="test_db",
            user="test_user",
            password="test_pass",
        )

        url = config.database_url
        assert "postgresql+asyncpg://" in url
        assert "test_user:test_pass@localhost:5432/test_db" in url

    def test_database_url_from_url_field(self):
        """Test database_url when url field is provided."""
        config = DatabaseConfig(
            url="postgresql+asyncpg://user:pass@host:5432/db",
        )

        assert config.database_url == "postgresql+asyncpg://user:pass@host:5432/db"

    def test_sync_database_url(self):
        """Test sync_database_url property."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            name="test_db",
            user="test_user",
            password="test_pass",
        )

        url = config.sync_database_url
        assert "postgresql://" in url
        assert "+asyncpg" not in url
        assert "test_user:test_pass@localhost:5432/test_db" in url


class TestRedisConfig:
    """Tests for RedisConfig."""

    def test_default_values(self):
        """Test RedisConfig default values."""
        config = RedisConfig()

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.password is None

    def test_load_from_environment(self):
        """Test loading RedisConfig from environment variables."""
        os.environ["REDIS_HOST"] = "redis-host"
        os.environ["REDIS_PORT"] = "6380"
        os.environ["REDIS_PASSWORD"] = "redis_pass"

        config = RedisConfig()

        assert config.host == "redis-host"
        assert config.port == 6380
        assert config.password == "redis_pass"

        # Cleanup
        os.environ.pop("REDIS_HOST", None)
        os.environ.pop("REDIS_PORT", None)
        os.environ.pop("REDIS_PASSWORD", None)

    def test_redis_url_property(self):
        """Test redis_url property generation."""
        config = RedisConfig(
            host="localhost",
            port=6379,
            db=0,
        )

        url = config.redis_url
        assert url == "redis://localhost:6379/0"

    def test_redis_url_with_password(self):
        """Test redis_url with password."""
        config = RedisConfig(
            host="localhost",
            port=6379,
            db=0,
            password="secret",
        )

        url = config.redis_url
        assert "redis://:secret@localhost:6379/0" in url


class TestAPIConfig:
    """Tests for APIConfig."""

    def test_default_values(self):
        """Test APIConfig default values."""
        config = APIConfig()

        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.workers == 4
        assert config.reload is True

    def test_load_from_environment(self):
        """Test loading APIConfig from environment variables."""
        os.environ["API_HOST"] = "127.0.0.1"
        os.environ["API_PORT"] = "9000"
        os.environ["API_WORKERS"] = "8"

        config = APIConfig()

        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.workers == 8

        # Cleanup
        os.environ.pop("API_HOST", None)
        os.environ.pop("API_PORT", None)
        os.environ.pop("API_WORKERS", None)
