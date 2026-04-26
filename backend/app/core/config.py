"""Application configuration settings."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Get the project root (parent of backend directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


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

    # Upload settings - use absolute path from project root
    UPLOAD_DIR: str = str(PROJECT_ROOT / "uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AI settings (OpenRouter)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "google/gemma-4-31b-it:free"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()