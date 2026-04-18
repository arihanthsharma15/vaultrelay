import os
import pytest
from pydantic import ValidationError
from app.core.config import Settings

# Set required env vars for module-level settings import
os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"


def test_settings_loads_from_env():
    s = Settings(
        _env_file=None,
        secret_key="my-secret",
        database_url="postgresql://test:test@localhost/test",
    )
    assert s.secret_key == "my-secret"
    assert s.app_env == "development"
    assert s.app_port == 8000


def test_settings_missing_secret_key():
    old = os.environ.pop("SECRET_KEY", None)
    try:
        with pytest.raises(ValidationError):
            Settings(_env_file=None,
                     database_url="postgresql://test:test@localhost/test")
    finally:
        if old:
            os.environ["SECRET_KEY"] = old


def test_settings_missing_database_url():
    old = os.environ.pop("DATABASE_URL", None)
    try:
        with pytest.raises(ValidationError):
            Settings(_env_file=None,
                     secret_key="test-secret")
    finally:
        if old:
            os.environ["DATABASE_URL"] = old
