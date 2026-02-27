from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import (
    UUID as SA_UUID,
    Boolean,
    Column,
    Enum,
    String,
    Table,
)

from account.domain.account.enums import AccountRole
from shared.infrastructure.persistence.registry import mapper_registry


@dataclass(eq=False, kw_only=True)
class AccountMetadataRecord:
    account_id: UUID
    role: AccountRole
    is_active: bool


account_metadata_table = Table(
    "account_metadata",
    mapper_registry.metadata,
    Column("account_id", SA_UUID(as_uuid=True), primary_key=True),
    Column(
        "role",
        Enum(AccountRole, name="accountrole", create_type=False),
        default=AccountRole.USER,
        nullable=False,
    ),
    Column("is_active", Boolean, default=True, nullable=False),
)

# Read-only reference to auth.users for cross-schema joins
auth_users_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", SA_UUID(as_uuid=True), primary_key=True),
    Column("email", String(255), nullable=True),
    schema="auth",
    extend_existing=True,
)


def map_account_metadata_table() -> None:
    mapper_registry.map_imperatively(
        AccountMetadataRecord,
        account_metadata_table,
    )
