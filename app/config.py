"""Configuration module for FastForm. Loads environment variables and provides access to
settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class APIKeys(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="API_KEY_", extra="allow"
    )
    openai: str | None = None


class DatabaseConfig(BaseSettings):
    """Database configuration loaded from environment variables."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="DB_", extra="allow"
    )
    # Default to SQLite for containerized deployment
    url: str = "sqlite:///./fastform.db"
    pool_kwargs: dict[str, str | int | bool] | None = None


class AppConfig(BaseSettings):
    """Configuration and settings for the application."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="APP_", extra="allow"
    )

    # App
    name: str | None = "FastpeerAI FastForm"
    version: str | None = None

    # CORS
    cors_allow_credentials: bool = True
    cors_allow_origins: list[str] = ["*"]
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Production
    docs_enabled: bool = False
    dev_mode: bool = False
