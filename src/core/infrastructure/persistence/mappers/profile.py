from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import (
    UUID as SA_UUID,
    Column,
    ForeignKey,
    String,
    Table,
)

from core.domain.profile.value_objects import Username
from shared.infrastructure.persistence.registry import mapper_registry


@dataclass(eq=False, kw_only=True)
class ProfileRecord:
    id: UUID
    account_id: UUID
    username: str | None


profiles_table = Table(
    "profiles",
    mapper_registry.metadata,
    Column("id", SA_UUID(as_uuid=True), primary_key=True),
    Column(
        "account_id",
        SA_UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False,
        unique=True,
    ),
    Column("username", String(Username.MAX_LEN), nullable=True, unique=True),
)


def map_profiles_table() -> None:
    mapper_registry.map_imperatively(ProfileRecord, profiles_table)
