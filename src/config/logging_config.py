"""Logging configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseSettings):
    """Logging configuration."""

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        case_sensitive=False,
        extra="ignore",
    )

    level: str = Field(
        default="INFO",
        description="Logging level",
    )
    format: str = Field(
        default="json",
        description="Log format (json, text)",
    )
    file_path: str | None = Field(
        default=None,
        description="Log file path (None for console only)",
    )
    max_bytes: int = Field(
        default=10485760,  # 10MB
        description="Maximum log file size in bytes",
    )
    backup_count: int = Field(
        default=5,
        description="Number of backup log files to keep",
        ge=1,
    )
