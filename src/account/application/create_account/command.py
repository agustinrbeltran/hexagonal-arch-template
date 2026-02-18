from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from account.domain.account.enums import AccountRole


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateAccountCommand:
    email: str
    password: str
    role: AccountRole


class CreateAccountResponse(TypedDict):
    id: UUID
