import pytest
from pydantic import ValidationError

from shared.infrastructure.config.settings.security import AuthSettings
from tests.app.unit.factories.settings_data import create_auth_settings_data


def test_auth_settings_valid() -> None:
    data = create_auth_settings_data()

    sut = AuthSettings.model_validate(data)

    assert sut.access_token_expiry_min == 15


def test_auth_settings_custom_expiry() -> None:
    data = create_auth_settings_data(access_token_expiry_min=30)

    sut = AuthSettings.model_validate(data)

    assert sut.access_token_expiry_min == 30


@pytest.mark.parametrize(
    "field_override",
    [
        pytest.param({"ACCESS_TOKEN_EXPIRY_MIN": 0}, id="expiry_min_too_small"),
    ],
)
def test_auth_rejects_invalid_expiry(field_override: dict[str, int]) -> None:
    data = {**create_auth_settings_data(), **field_override}

    with pytest.raises(ValidationError):
        AuthSettings.model_validate(data)
