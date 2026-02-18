from typing import Any

from account.domain.account.enums import AccountRole
from account.domain.account.value_objects import Email
from shared.domain.account_id import AccountId
from shared.domain.errors import DomainError


class EmailAlreadyExistsError(DomainError):
    def __init__(self, email: Any) -> None:
        message = f"Account with {email!r} already exists."
        super().__init__(message)


class AccountNotFoundByIdError(DomainError):
    def __init__(self, account_id: AccountId) -> None:
        message = f"Account with {account_id.value!r} is not found."
        super().__init__(message)


class AccountNotFoundByEmailError(DomainError):
    def __init__(self, email: Email) -> None:
        message = f"Account with {email.value!r} is not found."
        super().__init__(message)


class ActivationChangeNotPermittedError(DomainError):
    def __init__(self, email: Email, role: AccountRole) -> None:
        message = (
            f"Changing activation of account {email.value!r} ({role}) is not permitted."
        )
        super().__init__(message)


class RoleAssignmentNotPermittedError(DomainError):
    def __init__(self, role: AccountRole) -> None:
        message = f"Assignment of role {role} is not permitted."
        super().__init__(message)


class RoleChangeNotPermittedError(DomainError):
    def __init__(self, email: Email, role: AccountRole) -> None:
        message = f"Changing role of account {email.value!r} ({role}) is not permitted."
        super().__init__(message)
