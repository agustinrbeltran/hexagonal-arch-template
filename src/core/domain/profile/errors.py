from typing import Any

from shared.domain.account_id import AccountId
from shared.domain.errors import DomainError

from core.domain.profile.value_objects import ProfileId


class ProfileNotFoundByIdError(DomainError):
    def __init__(self, profile_id: ProfileId) -> None:
        message = f"Profile with {profile_id.value!r} is not found."
        super().__init__(message)


class ProfileNotFoundByAccountIdError(DomainError):
    def __init__(self, account_id: AccountId) -> None:
        message = f"Profile for account {account_id.value!r} is not found."
        super().__init__(message)


class UsernameAlreadyExistsError(DomainError):
    def __init__(self, username: Any) -> None:
        message = f"Profile with username {username!r} already exists."
        super().__init__(message)
