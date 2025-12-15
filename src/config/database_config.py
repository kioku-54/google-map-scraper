"""Database configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """PostgreSQL + PostGIS database configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        case_sensitive=False,
        extra="ignore",
    )

    # Connection details
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="gmaps_scraper", description="Database name")
    user: str = Field(default="user", description="Database user")
    password: str = Field(default="password", description="Database password")

    # Connection pool settings
    pool_size: int = Field(default=10, description="Connection pool size")
    max_overflow: int = Field(default=20, description="Max overflow connections")
    pool_timeout: int = Field(default=30, description="Pool timeout in seconds")
    pool_recycle: int = Field(default=3600, description="Pool recycle time in seconds")

    # Full connection URL
    url: str | None = Field(
        default=None,
        description="Full database URL (postgresql+asyncpg://...)",
    )


    @property
    def database_url(self) -> str:
        """Get the full database URL."""
        if self.url:
            return self.url
        return f"""
            postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}
        """


    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for Alembic."""
        if self.url:
            # Replace asyncpg with psycopg2 for sync operations
            return self.url.replace("+asyncpg", "")
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
