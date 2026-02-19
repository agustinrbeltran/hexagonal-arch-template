import pytest

from account.domain.account.value_objects import Email
from shared.domain.errors import DomainTypeError


@pytest.mark.parametrize(
    "email",
    [
        pytest.param("a@example.com", id="simple"),
        pytest.param("a" * 243 + "@example.com", id="max_len"),
    ],
)
def test_accepts_valid_emails(email: str) -> None:
    Email(email)


@pytest.mark.parametrize(
    "email",
    [
        pytest.param("a" * 244 + "@example.com", id="too_long"),
        pytest.param("invalid", id="no_at_sign"),
        pytest.param("@example.com", id="no_local_part"),
        pytest.param("user@", id="no_domain"),
        pytest.param("user@.com", id="dot_start_domain"),
    ],
)
def test_rejects_invalid_emails(email: str) -> None:
    with pytest.raises(DomainTypeError):
        Email(email)
