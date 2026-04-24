"""Application configuration settings."""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # App settings
    APP_NAME: str = "Bug Report AI"
    APP_ENV: str = "development"
    API_PREFIX: str = "/api"

    # Database settings
    DATABASE_URL: str = "sqlite:///./bug_report.db"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()