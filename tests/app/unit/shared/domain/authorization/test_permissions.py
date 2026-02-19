import pytest

from account.domain.account.enums import AccountRole
from account.domain.account.services import (
    AccountManagementContext,
    CanManageRole,
    CanManageSelf,
    CanManageSubordinate,
    RoleManagementContext,
)
from tests.app.unit.factories.account_entity import create_account
from tests.app.unit.factories.value_objects import create_account_id


def test_can_manage_self() -> None:
    account_id = create_account_id()
    subject = create_account(account_id=account_id)
    target = create_account(account_id=account_id)
    context = AccountManagementContext(subject=subject, target=target)
    sut = CanManageSelf()

    assert sut.is_satisfied_by(context)


def test_cannot_manage_another_account() -> None:
    subject_id = create_account_id()
    subject = create_account(account_id=subject_id)
    target_id = create_account_id()
    target = create_account(account_id=target_id)
    context = AccountManagementContext(subject=subject, target=target)
    sut = CanManageSelf()

    assert not sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_role", "target_role"),
    [
        (AccountRole.SUPER_ADMIN, AccountRole.ADMIN),
        (AccountRole.SUPER_ADMIN, AccountRole.USER),
        (AccountRole.ADMIN, AccountRole.USER),
    ],
)
def test_can_manage_subordinate(
    subject_role: AccountRole,
    target_role: AccountRole,
) -> None:
    subject = create_account(role=subject_role)
    target = create_account(role=target_role)
    context = AccountManagementContext(subject=subject, target=target)
    sut = CanManageSubordinate()

    assert sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_role", "target_role"),
    [
        (AccountRole.SUPER_ADMIN, AccountRole.SUPER_ADMIN),
        (AccountRole.ADMIN, AccountRole.SUPER_ADMIN),
        (AccountRole.ADMIN, AccountRole.ADMIN),
        (AccountRole.USER, AccountRole.ADMIN),
    ],
)
def test_cannot_manage_non_subordinate(
    subject_role: AccountRole,
    target_role: AccountRole,
) -> None:
    subject = create_account(role=subject_role)
    target = create_account(role=target_role)
    context = AccountManagementContext(subject=subject, target=target)
    sut = CanManageSubordinate()

    assert not sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_role", "target_role"),
    [
        (AccountRole.SUPER_ADMIN, AccountRole.ADMIN),
        (AccountRole.SUPER_ADMIN, AccountRole.USER),
        (AccountRole.ADMIN, AccountRole.USER),
    ],
)
def test_can_manage_role(
    subject_role: AccountRole,
    target_role: AccountRole,
) -> None:
    subject = create_account(role=subject_role)
    context = RoleManagementContext(subject=subject, target_role=target_role)
    sut = CanManageRole()

    assert sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_role", "target_role"),
    [
        (AccountRole.SUPER_ADMIN, AccountRole.SUPER_ADMIN),
        (AccountRole.ADMIN, AccountRole.SUPER_ADMIN),
        (AccountRole.ADMIN, AccountRole.ADMIN),
        (AccountRole.USER, AccountRole.ADMIN),
    ],
)
def test_cannot_manage_role(
    subject_role: AccountRole,
    target_role: AccountRole,
) -> None:
    subject = create_account(role=subject_role)
    context = RoleManagementContext(subject=subject, target_role=target_role)
    sut = CanManageRole()

    assert not sut.is_satisfied_by(context)
