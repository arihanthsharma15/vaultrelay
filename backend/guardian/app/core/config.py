from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "VaultRelay Guardian"
    app_env: str = "development"
    app_port: int = 8000

    # Security
    secret_key: str

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"


@lru_cache
def get_settings() -> Settings:
    return Settings()
