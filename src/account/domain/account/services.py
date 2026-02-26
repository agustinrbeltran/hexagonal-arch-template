from collections.abc import Mapping
from dataclasses import dataclass

from account.domain.account.entity import Account
from account.domain.account.enums import SUBORDINATE_ROLES, AccountRole
from shared.domain.authorization import AnyOf, Permission, PermissionContext, authorize

# --- Account-specific permissions ---


@dataclass(frozen=True, kw_only=True)
class AccountManagementContext(PermissionContext):
    subject: Account
    target: Account


class CanManageSelf(Permission[AccountManagementContext]):
    def is_satisfied_by(self, context: AccountManagementContext) -> bool:
        return context.subject == context.target


class CanManageSubordinate(Permission[AccountManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[AccountRole, set[AccountRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: AccountManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target.role in allowed_roles


@dataclass(frozen=True, kw_only=True)
class RoleManagementContext(PermissionContext):
    subject: Account
    target_role: AccountRole


class CanManageRole(Permission[RoleManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[AccountRole, set[AccountRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: RoleManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target_role in allowed_roles


# Re-export authorize and AnyOf for convenience
__all__ = [
    "AccountManagementContext",
    "AnyOf",
    "CanManageRole",
    "CanManageSelf",
    "CanManageSubordinate",
    "RoleManagementContext",
    "authorize",
]
