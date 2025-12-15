"""H3 geospatial configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class H3Config(BaseSettings):
    """H3 geospatial indexing configuration."""

    model_config = SettingsConfigDict(
        env_prefix="H3_",
        case_sensitive=False,
        extra="ignore",
    )

    resolution: int = Field(
        default=9,
        description="H3 resolution level (0-15)",
        ge=0,
        le=15,
    )

    # Default resolution for different operations
    search_resolution: int = Field(
        default=9,
        description="H3 resolution for search operations",
        ge=0,
        le=15,
    )
    storage_resolution: int = Field(
        default=9,
        description="H3 resolution for storage",
        ge=0,
        le=15,
    )
