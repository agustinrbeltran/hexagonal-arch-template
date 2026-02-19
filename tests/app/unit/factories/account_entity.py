from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.value_objects import AccountPasswordHash, Email
from shared.domain.account_id import AccountId
from tests.app.unit.factories.value_objects import (
    create_account_id,
    create_email,
    create_password_hash,
)


def create_account(
    account_id: AccountId | None = None,
    email: Email | None = None,
    password_hash: AccountPasswordHash | None = None,
    role: AccountRole = AccountRole.USER,
    is_active: bool = True,
) -> Account:
    return Account(
        id_=account_id or create_account_id(),
        email=email or create_email(),
        password_hash=password_hash or create_password_hash(),
        role=role,
        is_active=is_active,
    )
