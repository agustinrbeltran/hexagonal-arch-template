from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from core.application.get_my_profile.handler import GetMyProfileHandler
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from core.domain.profile.repository import ProfileRepository
from shared.domain.ports.identity_provider import IdentityProvider
from tests.app.unit.factories.profile_entity import create_profile
from tests.app.unit.factories.value_objects import (
    create_account_id,
    create_username,
)


@pytest.mark.asyncio
async def test_returns_profile_with_username() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)

    account_id = create_account_id()
    username = create_username("alice123")
    profile = create_profile(account_id=account_id, username=username)

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = GetMyProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
    )

    result = await sut.execute()

    assert result["id"] == profile.id_.value
    assert result["account_id"] == account_id.value
    assert result["username"] == username.value


@pytest.mark.asyncio
async def test_returns_profile_without_username() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)

    account_id = create_account_id()
    profile = create_profile(account_id=account_id, username=None)

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = GetMyProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
    )

    result = await sut.execute()

    assert result["username"] is None


@pytest.mark.asyncio
async def test_profile_not_found_raises_error() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)

    account_id = create_account_id()

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = None

    sut = GetMyProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
    )

    with pytest.raises(ProfileNotFoundByAccountIdError):
        await sut.execute()
