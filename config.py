"""Bot configuration using pydantic-settings."""

import json
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    BOT_TOKEN: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./moliyabot.db"

    # Admin
    ADMIN_IDS: str = "[]"

    # Scheduler
    DEFAULT_REMINDER_HOUR: int = 21
    DEFAULT_REMINDER_MINUTE: int = 0

    # Limits
    MAX_CATEGORIES: int = 20
    FREE_CATEGORIES: int = 15

    @property
    def admin_ids(self) -> list[int]:
        """Parse admin IDs from JSON string."""
        try:
            return json.loads(self.ADMIN_IDS)
        except (json.JSONDecodeError, TypeError):
            return []

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite."""
        return "sqlite" in self.DATABASE_URL

    @property
    def base_dir(self) -> Path:
        """Project base directory."""
        return Path(__file__).parent


settings = Settings()
