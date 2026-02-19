import uuid
from dataclasses import dataclass
from uuid import UUID

from account.domain.account.value_objects import AccountPasswordHash, Email, RawPassword
from core.domain.profile.value_objects import ProfileId, Username
from shared.domain.account_id import AccountId
from shared.domain.value_object import ValueObject


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


def create_account_id(value: UUID | None = None) -> AccountId:
    return AccountId(value if value else uuid.uuid4())


def create_email(value: str = "alice@example.com") -> Email:
    return Email(value)


def create_raw_password(value: str = "Good Password") -> RawPassword:
    return RawPassword(value)


def create_password_hash(value: bytes = b"password_hash") -> AccountPasswordHash:
    return AccountPasswordHash(value)


def create_profile_id(value: UUID | None = None) -> ProfileId:
    return ProfileId(value if value else uuid.uuid4())


def create_username(value: str = "alice123") -> Username:
    return Username(value)
