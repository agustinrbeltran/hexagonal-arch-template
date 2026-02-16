from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from domain.shared.errors import AuthorizationError
from domain.user.entity import User
from domain.user.enums import SUBORDINATE_ROLES, UserRole
from domain.user.ports import PasswordHasher, UserIdGenerator
from domain.user.value_objects import RawPassword, Username, UserPasswordHash

AUTHZ_NOT_AUTHORIZED: Final[str] = "Not authorized."


# --- Permission framework (pure domain, no framework deps) ---


@dataclass(frozen=True)
class PermissionContext:
    pass


class Permission[PC: PermissionContext](ABC):
    @abstractmethod
    def is_satisfied_by(self, context: PC) -> bool: ...


class AnyOf[PC: PermissionContext](Permission[PC]):
    def __init__(self, *permissions: Permission[PC]) -> None:
        self._permissions = permissions

    def is_satisfied_by(self, context: PC) -> bool:
        return any(p.is_satisfied_by(context) for p in self._permissions)


def authorize[PC: PermissionContext](
    permission: Permission[PC],
    *,
    context: PC,
) -> None:
    """:raises AuthorizationError:"""
    if not permission.is_satisfied_by(context):
        raise AuthorizationError(AUTHZ_NOT_AUTHORIZED)


# --- User-specific permissions ---


@dataclass(frozen=True, kw_only=True)
class UserManagementContext(PermissionContext):
    subject: User
    target: User


class CanManageSelf(Permission[UserManagementContext]):
    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        return context.subject == context.target


class CanManageSubordinate(Permission[UserManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[UserRole, set[UserRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target.role in allowed_roles


@dataclass(frozen=True, kw_only=True)
class RoleManagementContext(PermissionContext):
    subject: User
    target_role: UserRole


class CanManageRole(Permission[RoleManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[UserRole, set[UserRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: RoleManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target_role in allowed_roles


# --- Domain service ---


class UserService:
    def __init__(
        self,
        user_id_generator: UserIdGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher

    async def create(
        self,
        username: Username,
        raw_password: RawPassword,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        """
        :raises RoleAssignmentNotPermittedError:
        :raises PasswordHasherBusyError:
        """
        user_id = self._user_id_generator.generate()
        password_hash = await self._password_hasher.hash(raw_password)
        return User.create(
            id_=user_id,
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )

    async def is_password_valid(self, user: User, raw_password: RawPassword) -> bool:
        """:raises PasswordHasherBusyError:"""
        return await self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=user.password_hash,
        )

    async def change_password(self, user: User, raw_password: RawPassword) -> None:
        """:raises PasswordHasherBusyError:"""
        new_hash: UserPasswordHash = await self._password_hasher.hash(raw_password)
        user.change_password(new_hash)
