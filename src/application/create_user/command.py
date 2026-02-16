from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from domain.user.enums import UserRole


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserCommand:
    username: str
    password: str
    role: UserRole


class CreateUserResponse(TypedDict):
    id: UUID
