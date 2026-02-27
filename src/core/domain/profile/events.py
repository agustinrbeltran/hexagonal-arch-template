from dataclasses import dataclass
from datetime import date
from uuid import UUID

from shared.domain.domain_event import DomainEvent
from shared.domain.event_registry import register_event


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


@register_event
@dataclass(frozen=True, kw_only=True)
class ProfilePatchApplied(DomainEvent):
    profile_id: UUID
    first_name: tuple[str | None, str | None] | None = None
    last_name: tuple[str | None, str | None] | None = None
    birth_date: tuple[date | None, date | None] | None = None
    username: tuple[str | None, str | None] | None = None
