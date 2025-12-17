from dataclasses import dataclass

from common.domain.core.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UserPasswordHash(ValueObject):
    value: bytes
