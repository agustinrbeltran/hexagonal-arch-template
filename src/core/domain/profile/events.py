from dataclasses import dataclass
from uuid import UUID

from shared.domain.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ProfileCreated(DomainEvent):
    profile_id: UUID
    account_id: UUID
    username: str | None


@dataclass(frozen=True, kw_only=True)
class UsernameChanged(DomainEvent):
    profile_id: UUID
    old_username: str | None
    new_username: str
