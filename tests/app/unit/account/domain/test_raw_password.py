import pytest

from account.domain.account.value_objects import RawPassword
from shared.domain.errors import DomainTypeError


def test_accepts_boundary_length() -> None:
    password = "a" * RawPassword.MIN_LEN

    RawPassword(password)


def test_rejects_out_of_bounds_length() -> None:
    password = "a" * (RawPassword.MIN_LEN - 1)

    with pytest.raises(DomainTypeError):
        RawPassword(password)
