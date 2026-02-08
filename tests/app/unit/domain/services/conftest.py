from typing import cast
from unittest.mock import create_autospec

import pytest

from domain.user.ports import PasswordHasher
from domain.user.ports import UserIdGenerator
from tests.app.unit.domain.services.mock_types import (
    PasswordHasherMock,
    UserIdGeneratorMock,
)


@pytest.fixture
def user_id_generator() -> UserIdGeneratorMock:
    return cast(UserIdGeneratorMock, create_autospec(UserIdGenerator, instance=True))


@pytest.fixture
def password_hasher() -> PasswordHasherMock:
    return cast(PasswordHasherMock, create_autospec(PasswordHasher, instance=True))
