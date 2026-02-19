import pytest

from account.domain.account.enums import AccountRole


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (AccountRole.USER, True),
        (AccountRole.ADMIN, True),
        (AccountRole.SUPER_ADMIN, False),
    ],
)
def test_assignability(role: AccountRole, expected: bool) -> None:
    assert role.is_assignable is expected


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (AccountRole.USER, True),
        (AccountRole.ADMIN, True),
        (AccountRole.SUPER_ADMIN, False),
    ],
)
def test_changeability(role: AccountRole, expected: bool) -> None:
    assert role.is_changeable is expected
