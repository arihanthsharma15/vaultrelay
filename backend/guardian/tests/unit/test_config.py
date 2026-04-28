import os
import pytest
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
    )
    app_name: str = "VaultRelay Guardian"
    app_env: str = "development"
    app_port: int = 8000
    secret_key: str
    database_url: str
    redis_url: str = "redis://localhost:6379"


def test_settings_loads_correctly():
    s = AppSettings(
        secret_key="my-secret",
        database_url="postgresql://test:test@localhost/test",
    )
    assert s.secret_key == "my-secret"
    assert s.app_env == "development"
    assert s.app_port == 8000


def test_settings_missing_secret_key():
    env_backup = os.environ.copy()
    os.environ.clear()
    try:
        with pytest.raises(ValidationError):
            AppSettings(
                database_url="postgresql://test:test@localhost/test",
            )
    finally:
        os.environ.update(env_backup)


def test_settings_missing_database_url():
    env_backup = os.environ.copy()
    os.environ.clear()
    try:
        with pytest.raises(ValidationError):
            AppSettings(
                secret_key="test-secret",
            )
    finally:
        os.environ.update(env_backup)
