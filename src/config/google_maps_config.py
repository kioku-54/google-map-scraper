"""Google Maps specific configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleMapsConfig(BaseSettings):
    """Google Maps scraper configuration."""

    model_config = SettingsConfigDict(
        env_prefix="GOOGLE_MAPS_",
        case_sensitive=False,
        extra="ignore",
    )

    base_url: str = Field(
        default="https://www.google.com/maps",
        description="Google Maps base URL",
    )
    search_timeout: int = Field(
        default=30,
        description="Search page timeout in seconds",
        ge=1,
    )
    place_timeout: int = Field(
        default=30,
        description="Place detail page timeout in seconds",
        ge=1,
    )

    # Pagination settings
    max_results_per_search: int = Field(
        default=100,
        description="Maximum results per search query",
        ge=1,
        le=500,
    )
