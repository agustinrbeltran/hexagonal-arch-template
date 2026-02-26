from dataclasses import dataclass
from datetime import date
from uuid import UUID

from sqlalchemy import (
    UUID as SA_UUID,
    Column,
    Date,
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
    first_name: str | None
    last_name: str | None
    birth_date: date | None


profiles_table = Table(
    "profiles",
    mapper_registry.metadata,
    Column("id", SA_UUID(as_uuid=True), primary_key=True),
    Column(
        "account_id",
        SA_UUID(as_uuid=True),
        ForeignKey("auth.users.id"),
        nullable=False,
        unique=True,
    ),
    Column("username", String(Username.MAX_LEN), nullable=True, unique=True),
    Column("first_name", String(50), nullable=True),
    Column("last_name", String(50), nullable=True),
    Column("birth_date", Date, nullable=True),
)


def map_profiles_table() -> None:
    mapper_registry.map_imperatively(ProfileRecord, profiles_table)
