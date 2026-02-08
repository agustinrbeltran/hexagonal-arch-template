from dataclasses import dataclass
from uuid import UUID

from domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class SessionCreated(DomainEvent):
    session_id: str
    user_id: UUID


@dataclass(frozen=True, kw_only=True)
class SessionExpired(DomainEvent):
    session_id: str


@dataclass(frozen=True, kw_only=True)
class SessionRevoked(DomainEvent):
    session_id: str
