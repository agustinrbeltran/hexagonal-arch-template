from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import (
    UUID as SA_UUID,
    Boolean,
    Column,
    Enum,
    LargeBinary,
    String,
    Table,
)

from account.domain.account.enums import AccountRole
from account.domain.account.value_objects import Email
from shared.infrastructure.persistence.registry import mapper_registry


@dataclass(eq=False, kw_only=True)
class AccountRecord:
    id: UUID
    email: str
    password_hash: bytes
    role: AccountRole
    is_active: bool


accounts_table = Table(
    "accounts",
    mapper_registry.metadata,
    Column("id", SA_UUID(as_uuid=True), primary_key=True),
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
    mapper_registry.map_imperatively(AccountRecord, accounts_table)
