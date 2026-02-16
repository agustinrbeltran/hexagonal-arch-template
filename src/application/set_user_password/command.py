from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class SetUserPasswordCommand:
    user_id: UUID
    password: str
