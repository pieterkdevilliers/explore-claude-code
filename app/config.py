from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # JWT
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Local SQLite (admin users)
    local_db_url: str = "sqlite+aiosqlite:///./local.db"

    # Heroku Postgres (optional; written by /db-connection/save)
    database_url: Optional[str] = None


settings = Settings()
