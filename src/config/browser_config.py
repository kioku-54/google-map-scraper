"""Browser/Playwright configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BrowserConfig(BaseSettings):
    """Playwright browser configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BROWSER_",
        case_sensitive=False,
        extra="ignore",
    )

    browser_type: str = Field(
        default="chromium",
        description="Browser type (chromium, firefox, webkit)",
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )
    timeout: int = Field(
        default=30000,
        description="Default timeout in milliseconds",
        ge=1000,
    )
    navigation_timeout: int = Field(
        default=60000,
        description="Navigation timeout in milliseconds",
        ge=1000,
    )

    # Viewport settings
    viewport_width: int = Field(default=1920, description="Viewport width")
    viewport_height: int = Field(default=1080, description="Viewport height")

    # User agent
    user_agent: str | None = Field(
        default=None,
        description="Custom user agent string",
    )
