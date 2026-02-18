import pytest

from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.errors import (
    ActivationChangeNotPermittedError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
)
from account.domain.account.services import AccountService
from tests.app.unit.domain.services.mock_types import (
    AccountIdGeneratorMock,
    PasswordHasherMock,
)
from tests.app.unit.factories.user_entity import create_account
from tests.app.unit.factories.value_objects import (
    create_account_id,
    create_email,
    create_password_hash,
    create_raw_password,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role",
    [AccountRole.USER, AccountRole.ADMIN],
)
async def test_creates_active_account_with_hashed_password(
    role: AccountRole,
    account_id_generator: AccountIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    # Arrange
    email = create_email()
    raw_password = create_raw_password()

    expected_id = create_account_id()
    expected_hash = create_password_hash()

    account_id_generator.generate.return_value = expected_id
    password_hasher.hash.return_value = expected_hash
    sut = AccountService(account_id_generator, password_hasher)  # type: ignore[arg-type]

    # Act
    result = await sut.create(email, raw_password, role)

    # Assert
    assert isinstance(result, Account)
    assert result.id_ == expected_id
    assert result.email == email
    assert result.password_hash == expected_hash
    assert result.role == role
    assert result.is_active is True


@pytest.mark.asyncio
async def test_creates_inactive_account_if_specified(
    account_id_generator: AccountIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    email = create_email()
    raw_password = create_raw_password()
    sut = AccountService(account_id_generator, password_hasher)  # type: ignore[arg-type]

    result = await sut.create(email, raw_password, is_active=False)

    assert not result.is_active


@pytest.mark.asyncio
async def test_fails_to_create_account_with_unassignable_role(
    account_id_generator: AccountIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    email = create_email()
    raw_password = create_raw_password()
    sut = AccountService(account_id_generator, password_hasher)  # type: ignore[arg-type]

    with pytest.raises(RoleAssignmentNotPermittedError):
        await sut.create(
            email=email,
            raw_password=raw_password,
            role=AccountRole.SUPER_ADMIN,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "is_valid",
    [True, False],
)
async def test_checks_password_authenticity(
    is_valid: bool,
    account_id_generator: AccountIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    # Arrange
    account = create_account()
    raw_password = create_raw_password()

    password_hasher.verify.return_value = is_valid
    sut = AccountService(account_id_generator, password_hasher)  # type: ignore[arg-type]

    # Act
    result = await sut.is_password_valid(account, raw_password)

    # Assert
    assert result is is_valid


@pytest.mark.asyncio
async def test_changes_password(
    account_id_generator: AccountIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    # Arrange
    initial_hash = create_password_hash(b"old")
    account = create_account(password_hash=initial_hash)
    raw_password = create_raw_password()

    expected_hash = create_password_hash(b"new")
    password_hasher.hash.return_value = expected_hash
    sut = AccountService(account_id_generator, password_hasher)  # type: ignore[arg-type]

    # Act
    await sut.change_password(account, raw_password)

    # Assert
    assert account.password_hash == expected_hash


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
