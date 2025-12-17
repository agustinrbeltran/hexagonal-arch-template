import uuid
from dataclasses import dataclass
from uuid import UUID

from common.domain.core.value_objects.base import ValueObject
from features.user.domain.core.vo.raw_password import RawPassword
from features.user.domain.core.vo.user_id import UserId
from features.user.domain.core.vo.user_password_hash import UserPasswordHash
from features.user.domain.core.vo.username import Username


@dataclass(frozen=True, slots=True, repr=False)
class SingleFieldVO(ValueObject):
    value: int


@dataclass(frozen=True, slots=True, repr=False)
class MultiFieldVO(ValueObject):
    value1: int
    value2: str


def create_single_field_vo(value: int = 1) -> SingleFieldVO:
    return SingleFieldVO(value)


def create_multi_field_vo(value1: int = 1, value2: str = "Alice") -> MultiFieldVO:
    return MultiFieldVO(value1, value2)


def create_user_id(value: UUID | None = None) -> UserId:
    return UserId(value if value else uuid.uuid4())


def create_username(value: str = "Alice") -> Username:
    return Username(value)


def create_raw_password(value: str = "Good Password") -> RawPassword:
    return RawPassword(value)


def create_password_hash(value: bytes = b"password_hash") -> UserPasswordHash:
    return UserPasswordHash(value)
