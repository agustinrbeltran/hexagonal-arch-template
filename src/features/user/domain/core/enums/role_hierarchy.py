from collections.abc import Mapping
from typing import Final

from features.user.domain.core.enums.user_role import UserRole

SUBORDINATE_ROLES: Final[Mapping[UserRole, set[UserRole]]] = {
    UserRole.SUPER_ADMIN: {UserRole.ADMIN, UserRole.USER},
    UserRole.ADMIN: {UserRole.USER},
    UserRole.USER: set(),
}
