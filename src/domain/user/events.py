from dataclasses import dataclass
from uuid import UUID

from domain.shared.domain_event import DomainEvent
from domain.user.enums import UserRole


@dataclass(frozen=True, kw_only=True)
class UserCreated(DomainEvent):
    user_id: UUID
    username: str
    role: UserRole


@dataclass(frozen=True, kw_only=True)
class UserActivated(DomainEvent):
    user_id: UUID


@dataclass(frozen=True, kw_only=True)
class UserDeactivated(DomainEvent):
    user_id: UUID


@dataclass(frozen=True, kw_only=True)
class UserRoleChanged(DomainEvent):
    user_id: UUID
    old_role: UserRole
    new_role: UserRole


@dataclass(frozen=True, kw_only=True)
class UserPasswordChanged(DomainEvent):
    user_id: UUID
