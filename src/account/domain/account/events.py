from dataclasses import dataclass
from uuid import UUID

from account.domain.account.enums import AccountRole
from shared.domain.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class AccountCreated(DomainEvent):
    account_id: UUID
    email: str
    role: AccountRole


@dataclass(frozen=True, kw_only=True)
class AccountActivated(DomainEvent):
    account_id: UUID


@dataclass(frozen=True, kw_only=True)
class AccountDeactivated(DomainEvent):
    account_id: UUID


@dataclass(frozen=True, kw_only=True)
class AccountRoleChanged(DomainEvent):
    account_id: UUID
    old_role: AccountRole
    new_role: AccountRole


@dataclass(frozen=True, kw_only=True)
class AccountPasswordChanged(DomainEvent):
    account_id: UUID
