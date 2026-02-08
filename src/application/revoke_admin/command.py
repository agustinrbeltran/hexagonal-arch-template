from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RevokeAdminCommand:
    user_id: UUID
