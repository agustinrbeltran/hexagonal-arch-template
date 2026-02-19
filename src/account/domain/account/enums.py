from collections.abc import Mapping
from enum import StrEnum
from typing import Final


class AccountRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"

    @property
    def is_assignable(self) -> bool:
        return self != AccountRole.SUPER_ADMIN

    @property
    def is_changeable(self) -> bool:
        return self != AccountRole.SUPER_ADMIN


SUBORDINATE_ROLES: Final[Mapping[AccountRole, set[AccountRole]]] = {
    AccountRole.SUPER_ADMIN: {AccountRole.ADMIN, AccountRole.USER},
    AccountRole.ADMIN: {AccountRole.USER},
    AccountRole.USER: set(),
}
