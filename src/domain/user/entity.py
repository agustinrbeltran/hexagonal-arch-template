from domain.shared.aggregate_root import AggregateRoot
from domain.user.enums import UserRole
from domain.user.errors import (
    ActivationChangeNotPermittedError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
)
from domain.user.events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserPasswordChanged,
    UserRoleChanged,
)
from domain.user.value_objects import UserId, Username, UserPasswordHash


class User(AggregateRoot[UserId]):
    def __init__(
        self,
        *,
        id_: UserId,
        username: Username,
        password_hash: UserPasswordHash,
        role: UserRole,
        is_active: bool,
    ) -> None:
        super().__init__(id_=id_)
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active

    @classmethod
    def create(
        cls,
        *,
        id_: UserId,
        username: Username,
        password_hash: UserPasswordHash,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> "User":
        """:raises RoleAssignmentNotPermittedError:"""
        if not role.is_assignable:
            raise RoleAssignmentNotPermittedError(role)
        user = cls(
            id_=id_,
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        user._register_event(
            UserCreated(
                user_id=id_.value,
                username=username.value,
                role=role,
            )
        )
        return user

    def activate(self) -> bool:
        """:raises ActivationChangeNotPermittedError:"""
        if not self.role.is_changeable:
            raise ActivationChangeNotPermittedError(self.username, self.role)
        if self.is_active:
            return False
        self.is_active = True
        self._register_event(UserActivated(user_id=self.id_.value))
        return True

    def deactivate(self) -> bool:
        """:raises ActivationChangeNotPermittedError:"""
        if not self.role.is_changeable:
            raise ActivationChangeNotPermittedError(self.username, self.role)
        if not self.is_active:
            return False
        self.is_active = False
        self._register_event(UserDeactivated(user_id=self.id_.value))
        return True

    def change_role(self, new_role: UserRole) -> bool:
        """:raises RoleChangeNotPermittedError:"""
        if not self.role.is_changeable:
            raise RoleChangeNotPermittedError(self.username, self.role)
        if self.role == new_role:
            return False
        old_role = self.role
        self.role = new_role
        self._register_event(
            UserRoleChanged(
                user_id=self.id_.value,
                old_role=old_role,
                new_role=new_role,
            )
        )
        return True

    def change_password(self, new_hash: UserPasswordHash) -> None:
        self.password_hash = new_hash
        self._register_event(UserPasswordChanged(user_id=self.id_.value))
