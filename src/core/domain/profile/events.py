from dataclasses import dataclass
from datetime import date
from uuid import UUID

from shared.domain.domain_event import DomainEvent
from shared.infrastructure.events.registry import register_event


@register_event
@dataclass(frozen=True, kw_only=True)
class ProfileCreated(DomainEvent):
    profile_id: UUID
    account_id: UUID
    username: str | None


@register_event
@dataclass(frozen=True, kw_only=True)
class ProfileUpdated(DomainEvent):
    profile_id: UUID
    old_first_name: str | None
    new_first_name: str | None
    old_last_name: str | None
    new_last_name: str | None
    old_birth_date: date | None
    new_birth_date: date | None
    old_username: str | None
    new_username: str | None
