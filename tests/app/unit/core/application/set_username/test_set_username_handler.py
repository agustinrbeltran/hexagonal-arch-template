from typing import cast
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest

from core.application.set_username.command import SetUsernameCommand
from core.application.set_username.handler import SetUsernameHandler
from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from core.domain.profile.repository import ProfileRepository
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.ports.identity_provider import IdentityProvider
from tests.app.unit.factories.profile_entity import create_profile
from tests.app.unit.factories.value_objects import create_account_id


@pytest.mark.asyncio
async def test_sets_username_successfully() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    profile = create_profile(account_id=account_id, username=None)
    command = SetUsernameCommand(username="newuser1")

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = SetUsernameHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    assert profile.username is not None
    assert profile.username.value == "newuser1"
    cast(AsyncMock, core_unit_of_work.commit).assert_awaited_once()
    cast(AsyncMock, event_dispatcher.dispatch).assert_awaited_once()


@pytest.mark.asyncio
async def test_profile_not_found_raises_error() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    command = SetUsernameCommand(username="newuser1")

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = None

    sut = SetUsernameHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(ProfileNotFoundByAccountIdError):
        await sut.execute(command)


@pytest.mark.asyncio
async def test_for_update_forwarded_to_repo() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    profile = create_profile(account_id=account_id, username=None)
    command = SetUsernameCommand(username="newuser1")

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = SetUsernameHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    cast(AsyncMock, profile_repository.get_by_account_id).assert_awaited_once_with(
        account_id, for_update=True
    )


@pytest.mark.asyncio
async def test_save_is_called_with_updated_profile() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    profile = create_profile(account_id=account_id, username=None)
    command = SetUsernameCommand(username="newuser1")

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = SetUsernameHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    cast(MagicMock, profile_repository.save).assert_called_once_with(profile)
    assert profile.username is not None
    assert profile.username.value == "newuser1"
