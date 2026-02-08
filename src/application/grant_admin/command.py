from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GrantAdminCommand:
    user_id: UUID
