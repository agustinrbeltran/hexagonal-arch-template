from collections.abc import Mapping
from dataclasses import dataclass

from shared.domain.authorization import AnyOf, Permission, PermissionContext, authorize

from account.domain.account.entity import Account
from account.domain.account.enums import SUBORDINATE_ROLES, AccountRole
from account.domain.account.ports import AccountIdGenerator, PasswordHasher
from account.domain.account.value_objects import AccountPasswordHash, Email, RawPassword


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


# --- Domain service ---


class AccountService:
    def __init__(
        self,
        account_id_generator: AccountIdGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self._account_id_generator = account_id_generator
        self._password_hasher = password_hasher

    async def create(
        self,
        email: Email,
        raw_password: RawPassword,
        role: AccountRole = AccountRole.USER,
        is_active: bool = True,
    ) -> Account:
        """
        :raises RoleAssignmentNotPermittedError:
        :raises PasswordHasherBusyError:
        """
        account_id = self._account_id_generator.generate()
        password_hash = await self._password_hasher.hash(raw_password)
        return Account.create(
            id_=account_id,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )

    async def is_password_valid(
        self, account: Account, raw_password: RawPassword
    ) -> bool:
        """:raises PasswordHasherBusyError:"""
        return await self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=account.password_hash,
        )

    async def change_password(
        self, account: Account, raw_password: RawPassword
    ) -> None:
        """:raises PasswordHasherBusyError:"""
        new_hash: AccountPasswordHash = await self._password_hasher.hash(raw_password)
        account.change_password(new_hash)
