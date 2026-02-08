from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class SignUpCommand:
    username: str
    password: str


class SignUpResponse(TypedDict):
    id: UUID
