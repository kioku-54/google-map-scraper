"""Scraper configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScraperConfig(BaseSettings):
    """Scraper general configuration."""

    model_config = SettingsConfigDict(
        env_prefix="SCRAPER_",
        case_sensitive=False,
        extra="ignore",
    )

    concurrent_jobs: int = Field(
        default=5,
        description="Number of concurrent scraping jobs",
        ge=1,
        le=50,
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for failed jobs",
        ge=0,
    )
    timeout: int = Field(
        default=30,
        description="Default timeout for scraping operations in seconds",
        ge=1,
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting",
    )
    rate_limit_requests_per_second: float = Field(
        default=10.0,
        description="Requests per second limit",
        gt=0,
    )
    rate_limit_burst: int = Field(
        default=20,
        description="Burst limit for rate limiting",
        ge=1,
    )
