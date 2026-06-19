import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.audit_log import AuditLogData
from app.services.audit_logger import _redact_body, log_request


def make_mock_db() -> MagicMock:
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    return mock_db


@pytest.mark.asyncio
async def test_log_request_creates_audit_log():
    """Test that audit log is created with all fields."""
    mock_db = make_mock_db()

    audit_data = AuditLogData(
        tenant_id="tenant1",
        api_key_id="key1",
        endpoint="/v1/query",
        method="POST",
        status_code=200,
        request_body='{"question": "select * from users"}',
        response_summary="Success",
        duration_ms=100,
        ip_address="192.168.1.1",
        user_agent="curl/7.0",
    )

    result = await log_request(mock_db, audit_data)

    assert result is not None
    assert result.tenant_id == "tenant1"
    assert result.api_key_id == "key1"
    assert result.endpoint == "/v1/query"
    assert result.method == "POST"
    assert result.status_code == 200
    assert result.duration_ms == 100
    assert result.ip_address == "192.168.1.1"
    assert result.user_agent == "curl/7.0"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_log_request_redacts_passwords():
    """Test that passwords are redacted in request body."""
    mock_db = make_mock_db()

    audit_data = AuditLogData(
        tenant_id="tenant1",
        endpoint="/login",
        method="POST",
        request_body='{"username": "user", "password": "secret123"}',
        response_summary="Login success",
    )

    result = await log_request(mock_db, audit_data)

    if result:
        body = json.loads(result.request_body)
        assert body["username"] == "user"
        assert body["password"] == "[REDACTED]"


@pytest.mark.asyncio
async def test_log_request_redacts_api_keys():
    """Test that API keys are redacted."""
    mock_db = make_mock_db()

    audit_data = AuditLogData(
        tenant_id="tenant1",
        endpoint="/api/data",
        method="GET",
        request_body='{"api_key": "sk-12345", "query": "select 1"}',
        response_summary="Success",
    )

    result = await log_request(mock_db, audit_data)

    if result:
        body = json.loads(result.request_body)
        assert body["api_key"] == "[REDACTED]"
        assert body["query"] == "select 1"


@pytest.mark.asyncio
async def test_log_request_truncates_response_summary():
    """Test that response summary is truncated to 100 chars."""
    mock_db = make_mock_db()
    long_response = "x" * 200

    audit_data = AuditLogData(
        tenant_id="tenant1",
        endpoint="/v1/query",
        method="POST",
        response_summary=long_response,
    )

    result = await log_request(mock_db, audit_data)

    assert len(result.response_summary) == 100


@pytest.mark.asyncio
async def test_log_request_handles_invalid_json():
    """Test that invalid JSON in request body is stored as-is."""
    mock_db = make_mock_db()

    audit_data = AuditLogData(
        tenant_id="tenant1",
        endpoint="/v1/query",
        method="POST",
        request_body="not json",
        response_summary="Success",
    )

    result = await log_request(mock_db, audit_data)

    assert result.request_body == "not json"


@pytest.mark.asyncio
async def test_log_request_handles_db_error():
    """Test that DB errors are gracefully handled."""
    mock_db = make_mock_db()
    mock_db.commit.side_effect = Exception("DB error")

    audit_data = AuditLogData(
        tenant_id="tenant1",
        endpoint="/v1/query",
        method="POST",
    )

    result = await log_request(mock_db, audit_data)

    assert result is None
    mock_db.rollback.assert_called_once()


def test_redact_body_redacts_sensitive_keys():
    """Test that sensitive keys are redacted."""
    body = {
        "username": "user",
        "password": "secret",
        "api_key": "sk-123",
        "Authorization": "Bearer token",
        "query": "select 1",
    }

    redacted = _redact_body(body)

    assert redacted["username"] == "user"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["Authorization"] == "[REDACTED]"
    assert redacted["query"] == "select 1"


def test_redact_body_case_insensitive():
    """Test that key redaction is case-insensitive."""
    body = {
        "PASSWORD": "secret",
        "Password": "secret",
        "password": "secret",
    }

    redacted = _redact_body(body)

    assert redacted["PASSWORD"] == "[REDACTED]"
    assert redacted["Password"] == "[REDACTED]"
    assert redacted["password"] == "[REDACTED]"
