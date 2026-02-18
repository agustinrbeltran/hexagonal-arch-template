from sqlalchemy import UUID, Boolean, Column, Enum, LargeBinary, String, Table
from sqlalchemy.orm import composite

from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.value_objects import AccountPasswordHash, Email
from shared.domain.account_id import AccountId
from shared.infrastructure.persistence.registry import mapper_registry

accounts_table = Table(
    "accounts",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("email", String(Email.MAX_LEN), nullable=False, unique=True),
    Column("password_hash", LargeBinary, nullable=False),
    Column(
        "role",
        Enum(AccountRole, name="accountrole"),
        default=AccountRole.USER,
        nullable=False,
    ),
    Column("is_active", Boolean, default=True, nullable=False),
)


def map_accounts_table() -> None:
    mapper_registry.map_imperatively(
        Account,
        accounts_table,
        properties={
            "id_": composite(AccountId, accounts_table.c.id),
            "email": composite(Email, accounts_table.c.email),
            "password_hash": composite(
                AccountPasswordHash, accounts_table.c.password_hash
            ),
            "role": accounts_table.c.role,
            "is_active": accounts_table.c.is_active,
        },
        exclude_properties=["_events"],
        column_prefix="_",
    )
