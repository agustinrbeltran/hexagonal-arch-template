from shared.domain.account_id import AccountId
from shared.domain.aggregate_root import AggregateRoot

from account.domain.account.enums import AccountRole
from account.domain.account.errors import (
    ActivationChangeNotPermittedError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
)
from account.domain.account.events import (
    AccountActivated,
    AccountCreated,
    AccountDeactivated,
    AccountPasswordChanged,
    AccountRoleChanged,
)
from account.domain.account.value_objects import AccountPasswordHash, Email


class Account(AggregateRoot[AccountId]):
    def __init__(
        self,
        *,
        id_: AccountId,
        email: Email,
        password_hash: AccountPasswordHash,
        role: AccountRole,
        is_active: bool,
    ) -> None:
        super().__init__(id_=id_)
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active

    @classmethod
    def create(
        cls,
        *,
        id_: AccountId,
        email: Email,
        password_hash: AccountPasswordHash,
        role: AccountRole = AccountRole.USER,
        is_active: bool = True,
    ) -> "Account":
        """:raises RoleAssignmentNotPermittedError:"""
        if not role.is_assignable:
            raise RoleAssignmentNotPermittedError(role)
        account = cls(
            id_=id_,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        account._register_event(
            AccountCreated(
                account_id=id_.value,
                email=email.value,
                role=role,
            )
        )
        return account

    def activate(self) -> bool:
        """:raises ActivationChangeNotPermittedError:"""
        if not self.role.is_changeable:
            raise ActivationChangeNotPermittedError(self.email, self.role)
        if self.is_active:
            return False
        self.is_active = True
        self._register_event(AccountActivated(account_id=self.id_.value))
        return True

    def deactivate(self) -> bool:
        """:raises ActivationChangeNotPermittedError:"""
        if not self.role.is_changeable:
            raise ActivationChangeNotPermittedError(self.email, self.role)
        if not self.is_active:
            return False
        self.is_active = False
        self._register_event(AccountDeactivated(account_id=self.id_.value))
        return True

    def change_role(self, new_role: AccountRole) -> bool:
        """:raises RoleChangeNotPermittedError:"""
        if not self.role.is_changeable:
            raise RoleChangeNotPermittedError(self.email, self.role)
        if self.role == new_role:
            return False
        old_role = self.role
        self.role = new_role
        self._register_event(
            AccountRoleChanged(
                account_id=self.id_.value,
                old_role=old_role,
                new_role=new_role,
            )
        )
        return True

    def change_password(self, new_hash: AccountPasswordHash) -> None:
        self.password_hash = new_hash
        self._register_event(AccountPasswordChanged(account_id=self.id_.value))
