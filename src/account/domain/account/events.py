from dataclasses import dataclass
from uuid import UUID

from account.domain.account.enums import AccountRole
from shared.domain.domain_event import DomainEvent
from shared.domain.event_registry import register_event


@register_event
@dataclass(frozen=True, kw_only=True)
class AccountCreated(DomainEvent):
    account_id: UUID
    email: str
    role: AccountRole


@register_event
@dataclass(frozen=True, kw_only=True)
class AccountActivated(DomainEvent):
    account_id: UUID


@register_event
@dataclass(frozen=True, kw_only=True)
class AccountDeactivated(DomainEvent):
    account_id: UUID


@register_event
@dataclass(frozen=True, kw_only=True)
class AccountRoleChanged(DomainEvent):
    account_id: UUID
    old_role: AccountRole
    new_role: AccountRole
