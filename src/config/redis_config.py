"""Redis configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    """Redis configuration."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        case_sensitive=False,
        extra="ignore",
    )

    # Connection details
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    password: str | None = Field(default=None, description="Redis password")
    socket_timeout: int = Field(default=5, description="Socket timeout in seconds")

    # Full connection URL
    url: str | None = Field(
        default=None,
        description="Full Redis URL (redis://...)",
    )

    @property
    def redis_url(self) -> str:
        """Get the full Redis URL."""
        if self.url:
            return self.url
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"
