from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment and `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Customer Support Assistant"
    app_version: str = "1.0.0"
    environment: str = "local-dev"
    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    alembic_database_url: str = "sqlite:///./data/app.db"
    redis_url: str = "redis://localhost:6379/0"
    chroma_path: Path = Path("./data/chroma_db")
    upload_dir: Path = Path("./data/uploads")
    secret_key: str = Field(min_length=16, default="change-me-minimum-32-bytes")
    session_ttl_seconds: int = 86_400
    query_cache_ttl_seconds: int = 3_600
    rate_limit_per_minute: int = 60
    max_upload_bytes: int = 52_428_800
    llm_provider: str = "local"
    local_llm_base_url: str = "http://localhost:8080"
    local_llm_model: str = "gemma-4-2b-instruct"
    openrouter_api_key: str = ""
    openrouter_model: str = ""
    cors_origins: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Parse comma-separated CORS origins from environment variables."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
