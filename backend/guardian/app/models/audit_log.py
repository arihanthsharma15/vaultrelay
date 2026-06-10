import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tenants.id"),
    )
    api_key_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("api_keys.id"),
        nullable=True,
    )
    endpoint: Mapped[str] = mapped_column(String(255))
    method: Mapped[str] = mapped_column(String(10))
    status_code: Mapped[int] = mapped_column(default=200)
    request_body: Mapped[str | None] = mapped_column(nullable=True)
    response_summary: Mapped[str | None] = mapped_column(nullable=True)
    duration_ms: Mapped[int] = mapped_column(default=0)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, tenant_id={self.tenant_id}, "
            f"endpoint={self.endpoint}, method={self.method}, "
            f"status_code={self.status_code})>"
        )
