from dataclasses import dataclass
from uuid import UUID

from shared.domain.value_object import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class AccountId(ValueObject):
    value: UUID
