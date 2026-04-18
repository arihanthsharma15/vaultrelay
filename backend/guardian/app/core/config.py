from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_file_override=False,
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


settings = Settings()
