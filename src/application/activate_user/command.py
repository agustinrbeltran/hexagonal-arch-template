from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ActivateUserCommand:
    user_id: UUID
