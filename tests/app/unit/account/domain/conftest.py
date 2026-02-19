from typing import cast
from unittest.mock import create_autospec

import pytest

from account.domain.account.ports import AccountIdGenerator, PasswordHasher
from tests.app.unit.account.domain.mock_types import (
    AccountIdGeneratorMock,
    PasswordHasherMock,
)


@pytest.fixture
def account_id_generator() -> AccountIdGeneratorMock:
    return cast(
        AccountIdGeneratorMock, create_autospec(AccountIdGenerator, instance=True)
    )


@pytest.fixture
def password_hasher() -> PasswordHasherMock:
    return cast(PasswordHasherMock, create_autospec(PasswordHasher, instance=True))
