from pydantic import BaseModel


class AuditLogData(BaseModel):
    """Data for creating an audit log entry."""

    tenant_id: str
    api_key_id: str | None = None
    endpoint: str
    method: str
    status_code: int = 200
    request_body: str | None = None
    response_summary: str | None = None
    duration_ms: int = 0
    ip_address: str | None = None
    user_agent: str | None = None
