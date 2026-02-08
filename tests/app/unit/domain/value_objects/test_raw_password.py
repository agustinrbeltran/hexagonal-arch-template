import pytest

from domain.shared.errors import DomainTypeError
from domain.user.value_objects import RawPassword


def test_accepts_boundary_length() -> None:
    password = "a" * RawPassword.MIN_LEN

    RawPassword(password)


def test_rejects_out_of_bounds_length() -> None:
    password = "a" * (RawPassword.MIN_LEN - 1)

    with pytest.raises(DomainTypeError):
        RawPassword(password)
