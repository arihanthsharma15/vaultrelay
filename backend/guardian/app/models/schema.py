import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SchemaTable(Base):
    __tablename__ = "schema_tables"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tenants.id"),
        nullable=False,
    )
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    alias: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<SchemaTable {self.table_name}>"


class SchemaColumn(Base):
    __tablename__ = "schema_columns"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    table_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("schema_tables.id"),
        nullable=False,
    )
    column_name: Mapped[str] = mapped_column(String(255), nullable=False)
    column_type: Mapped[str] = mapped_column(String(100), nullable=False)
    alias: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_pii: Mapped[bool] = mapped_column(Boolean, default=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<SchemaColumn {self.column_name}>"
