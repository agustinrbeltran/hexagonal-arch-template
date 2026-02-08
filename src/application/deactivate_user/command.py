from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DeactivateUserCommand:
    user_id: UUID
