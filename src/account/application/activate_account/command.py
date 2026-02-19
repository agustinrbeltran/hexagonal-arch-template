from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ActivateAccountCommand:
    account_id: UUID
