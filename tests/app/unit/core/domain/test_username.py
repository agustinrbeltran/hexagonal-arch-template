import pytest

from core.domain.profile.value_objects import Username
from shared.domain.errors import DomainTypeError


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("a" * Username.MIN_LEN, id="min_length"),
        pytest.param("a" * Username.MAX_LEN, id="max_length"),
        pytest.param("user.name", id="with_dot"),
        pytest.param("user-name", id="with_hyphen"),
        pytest.param("user_name", id="with_underscore"),
        pytest.param("User123", id="mixed_alpha_digit"),
    ],
)
def test_accepts_valid_usernames(value: str) -> None:
    Username(value)


def test_rejects_too_short() -> None:
    value = "a" * (Username.MIN_LEN - 1)

    with pytest.raises(DomainTypeError):
        Username(value)


def test_rejects_too_long() -> None:
    value = "a" * (Username.MAX_LEN + 1)

    with pytest.raises(DomainTypeError):
        Username(value)


def test_rejects_starts_with_special_char() -> None:
    with pytest.raises(DomainTypeError):
        Username(".abcde")


def test_rejects_ends_with_special_char() -> None:
    with pytest.raises(DomainTypeError):
        Username("abcde.")


def test_rejects_disallowed_chars() -> None:
    with pytest.raises(DomainTypeError):
        Username("user@name")


def test_rejects_consecutive_specials() -> None:
    with pytest.raises(DomainTypeError):
        Username("user..name")
