from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    UUID as SA_UUID,
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from shared.infrastructure.persistence.registry import mapper_registry


@dataclass(eq=False, kw_only=True)
class OutboxRecord:
    id: UUID = field(default_factory=uuid4)
    event_type: str
    payload: str
    occurred_at: datetime
    delivered: bool = False
    delivered_at: datetime | None = None
    retry_count: int = 0


outbox_table = Table(
    "outbox",
    mapper_registry.metadata,
    Column("id", SA_UUID(as_uuid=True), primary_key=True),
    Column("event_type", Text, nullable=False),
    Column("payload", JSONB, nullable=False),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("delivered", Boolean, nullable=False, default=False),
    Column("delivered_at", DateTime(timezone=True), nullable=True),
    Column("retry_count", Integer, nullable=False, default=0),
    Index("ix_outbox_undelivered", "occurred_at", postgresql_where="delivered = false"),
)


def map_outbox_table() -> None:
    mapper_registry.map_imperatively(OutboxRecord, outbox_table)
