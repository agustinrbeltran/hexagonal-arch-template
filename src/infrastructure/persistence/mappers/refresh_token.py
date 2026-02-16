from sqlalchemy import UUID, Column, DateTime, String, Table
from sqlalchemy.orm import composite

from domain.refresh_token.entity import RefreshToken
from domain.user.value_objects import UserId
from infrastructure.persistence.registry import mapper_registry

refresh_tokens_table = Table(
    "refresh_tokens",
    mapper_registry.metadata,
    Column("id", String, primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("expiration", DateTime(timezone=True), nullable=False),
)


def map_refresh_tokens_table() -> None:
    mapper_registry.map_imperatively(
        RefreshToken,
        refresh_tokens_table,
        properties={
            "id_": refresh_tokens_table.c.id,
            "user_id": composite(UserId, refresh_tokens_table.c.user_id),
            "expiration": refresh_tokens_table.c.expiration,
        },
        column_prefix="_",
    )
