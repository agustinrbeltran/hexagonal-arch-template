import pytest

from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.errors import (
    ActivationChangeNotPermittedError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
)
from tests.app.unit.factories.account_entity import create_account
from tests.app.unit.factories.value_objects import create_account_id, create_email


@pytest.mark.parametrize(
    "role",
    [AccountRole.USER, AccountRole.ADMIN],
)
def test_creates_account_with_default_state(role: AccountRole) -> None:
    account_id = create_account_id()
    email = create_email()

    result = Account.create(id_=account_id, email=email, role=role)

    assert isinstance(result, Account)
    assert result.id_ == account_id
    assert result.email == email
    assert result.role == role
    assert result.is_active is True


def test_creates_inactive_account_if_specified() -> None:
    result = Account.create(
        id_=create_account_id(), email=create_email(), is_active=False
    )

    assert not result.is_active


def test_fails_to_create_account_with_unassignable_role() -> None:
    with pytest.raises(RoleAssignmentNotPermittedError):
        Account.create(
            id_=create_account_id(),
            email=create_email(),
            role=AccountRole.SUPER_ADMIN,
        )


@pytest.mark.parametrize(
    ("initial_state", "method", "expected_result"),
    [
        pytest.param(True, "deactivate", True, id="active_to_inactive"),
        pytest.param(False, "activate", True, id="inactive_to_active"),
        pytest.param(True, "activate", False, id="already_active"),
        pytest.param(False, "deactivate", False, id="already_inactive"),
    ],
)
def test_toggles_activation_state(
    initial_state: bool,
    method: str,
    expected_result: bool,
) -> None:
    account = create_account(is_active=initial_state)

    result = getattr(account, method)()

    assert result is expected_result


@pytest.mark.parametrize(
    "method",
    ["activate", "deactivate"],
)
def test_preserves_super_admin_activation_state(
    method: str,
) -> None:
    account = create_account(role=AccountRole.SUPER_ADMIN, is_active=True)

    with pytest.raises(ActivationChangeNotPermittedError):
        getattr(account, method)()


@pytest.mark.parametrize(
    ("initial_role", "target_role", "expected_result"),
    [
        pytest.param(AccountRole.USER, AccountRole.ADMIN, True, id="user_to_admin"),
        pytest.param(AccountRole.ADMIN, AccountRole.USER, True, id="admin_to_user"),
        pytest.param(AccountRole.USER, AccountRole.USER, False, id="already_user"),
        pytest.param(AccountRole.ADMIN, AccountRole.ADMIN, False, id="already_admin"),
    ],
)
def test_toggles_role(
    initial_role: AccountRole,
    target_role: AccountRole,
    expected_result: bool,
) -> None:
    account = create_account(role=initial_role)

    result = account.change_role(target_role)

    assert result is expected_result
    assert account.role == target_role


@pytest.mark.parametrize(
    "target_role",
    [AccountRole.USER, AccountRole.ADMIN],
)
def test_preserves_super_admin_role(
    target_role: AccountRole,
) -> None:
    account = create_account(role=AccountRole.SUPER_ADMIN)

    with pytest.raises(RoleChangeNotPermittedError):
        account.change_role(target_role)

    assert account.role == AccountRole.SUPER_ADMIN
