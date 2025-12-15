"""Main configuration module."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.api_config import APIConfig
from src.config.browser_config import BrowserConfig
from src.config.database_config import DatabaseConfig
from src.config.google_maps_config import GoogleMapsConfig
from src.config.h3_config import H3Config
from src.config.logging_config import LoggingConfig
from src.config.redis_config import RedisConfig
from src.config.scraper_config import ScraperConfig


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application metadata
    app_name: str = Field(default="google-map-scraper", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Debug mode")

    # Domain-specific configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    scraper: ScraperConfig = Field(default_factory=ScraperConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    google_maps: GoogleMapsConfig = Field(default_factory=GoogleMapsConfig)
    h3: H3Config = Field(default_factory=H3Config)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Proxy configuration (optional)
    use_proxy: bool = Field(default=False, description="Enable proxy usage")
    proxy_list: str | None = Field(
        default=None,
        description="Comma-separated list of proxy URLs",
    )
    proxy_rotation_enabled: bool = Field(
        default=False,
        description="Enable proxy rotation",
    )
    proxy_timeout: int = Field(
        default=10,
        description="Proxy timeout in seconds",
    )

    # Encryption configuration
    encryption_key: str | None = Field(
        default=None,
        description="Encryption key for sensitive data",
    )
    encryption_algorithm: str = Field(
        default="AES-256-GCM",
        description="Encryption algorithm",
    )

    # Monitoring & Metrics
    prometheus_enabled: bool = Field(
        default=False,
        description="Enable Prometheus metrics",
    )
    prometheus_port: int = Field(
        default=9090,
        description="Prometheus metrics port",
    )
    metrics_enabled: bool = Field(
        default=False,
        description="Enable application metrics",
    )

    # Job Queue configuration
    queue_batch_size: int = Field(
        default=10,
        description="Job queue batch size",
        ge=1,
    )
    queue_poll_interval: int = Field(
        default=5,
        description="Job queue poll interval in seconds",
        ge=1,
    )
    queue_max_workers: int = Field(
        default=5,
        description="Maximum queue workers",
        ge=1,
    )


# Global settings instance (singleton pattern)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None
