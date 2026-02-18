from sqlalchemy import UUID, Column, ForeignKey, String, Table
from sqlalchemy.orm import composite

from core.domain.profile.entity import Profile
from core.domain.profile.value_objects import ProfileId, Username
from shared.domain.account_id import AccountId
from shared.infrastructure.persistence.registry import mapper_registry

profiles_table = Table(
    "profiles",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "account_id",
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False,
        unique=True,
    ),
    Column("username", String(Username.MAX_LEN), nullable=True, unique=True),
)


def map_profiles_table() -> None:
    mapper_registry.map_imperatively(
        Profile,
        profiles_table,
        properties={
            "id_": composite(ProfileId, profiles_table.c.id),
            "account_id": composite(AccountId, profiles_table.c.account_id),
            "username": composite(Username, profiles_table.c.username),
        },
        exclude_properties=["_events"],
        column_prefix="_",
    )
