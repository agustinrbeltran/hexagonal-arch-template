from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class SetAccountPasswordCommand:
    account_id: UUID
    password: str
