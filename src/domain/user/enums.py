from collections.abc import Mapping
from enum import StrEnum
from typing import Final


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"

    @property
    def is_assignable(self) -> bool:
        return self != UserRole.SUPER_ADMIN

    @property
    def is_changeable(self) -> bool:
        return self != UserRole.SUPER_ADMIN


SUBORDINATE_ROLES: Final[Mapping[UserRole, set[UserRole]]] = {
    UserRole.SUPER_ADMIN: {UserRole.ADMIN, UserRole.USER},
    UserRole.ADMIN: {UserRole.USER},
    UserRole.USER: set(),
}
