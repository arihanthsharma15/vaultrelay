import json
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogData


async def log_request(db: AsyncSession, audit_data: AuditLogData) -> Optional[AuditLog]:
    """
    Log a request to the audit log.
    Fire-and-forget: errors are logged but don't block the response.
    """
    try:
        request_body = None
        if audit_data.request_body:
            try:
                body_obj = json.loads(audit_data.request_body)
                redacted_body = _redact_body(body_obj)
                request_body = json.dumps(redacted_body)
            except (json.JSONDecodeError, TypeError):
                request_body = audit_data.request_body

        response_summary = None
        if audit_data.response_summary:
            response_summary = audit_data.response_summary[:100]

        audit_log = AuditLog(
            tenant_id=audit_data.tenant_id,
            api_key_id=audit_data.api_key_id,
            endpoint=audit_data.endpoint,
            method=audit_data.method,
            status_code=audit_data.status_code,
            request_body=request_body,
            response_summary=response_summary,
            duration_ms=audit_data.duration_ms,
            ip_address=audit_data.ip_address,
            user_agent=audit_data.user_agent,
        )

        db.add(audit_log)
        await db.commit()
        return audit_log
    except Exception:
        await db.rollback()
        return None


def _redact_body(obj: dict) -> dict:
    """Redact sensitive fields in request body."""
    sensitive_keys = {
        "password",
        "token",
        "secret",
        "api_key",
        "Authorization",
        "X-API-Key",
    }

    redacted = {}
    for key, value in obj.items():
        if key.lower() in {k.lower() for k in sensitive_keys}:
            redacted[key] = "[REDACTED]"
        elif isinstance(value, str):
            redacted[key] = value
        elif isinstance(value, dict):
            redacted[key] = _redact_body(value)
        else:
            redacted[key] = value

    return redacted
