"""Application configuration."""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # App metadata
    app_name: str = "Focus Agent"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")

    # API settings
    api_prefix: str = "/api"
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://192.168.0.18:30085", "http://focus.localhost"],
        env="CORS_ORIGINS"
    )

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///app/data/focus_agent.db",
        env="DATABASE_URL"
    )

    # Redis
    redis_url: str = Field(
        default="redis://redis:6379",
        env="REDIS_URL"
    )
    redis_enabled: bool = True

    # Obsidian
    obsidian_vault_path: Optional[str] = Field(
        default="/obsidian-vault",
        env="OBSIDIAN_VAULT_PATH"
    )
    obsidian_sync_enabled: bool = Field(default=False, env="OBSIDIAN_SYNC_ENABLED")

    # External APIs
    claude_api_key: Optional[str] = Field(default=None, env="CLAUDE_API_KEY")
    github_client_id: Optional[str] = Field(default=None, env="GITHUB_CLIENT_ID")
    github_client_secret: Optional[str] = Field(default=None, env="GITHUB_CLIENT_SECRET")

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Pomodoro defaults
    pomodoro_work_duration: int = 25  # minutes
    pomodoro_short_break: int = 5
    pomodoro_long_break: int = 15
    pomodoro_sessions_until_long_break: int = 4

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
