from datetime import date
from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.application.update_profile.command import UpdateProfileCommand
from core.application.update_profile.handler import UpdateProfileHandler
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from core.domain.profile.repository import ProfileRepository
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.errors import DomainTypeError
from shared.domain.ports.identity_provider import IdentityProvider
from tests.app.unit.factories.profile_entity import create_profile
from tests.app.unit.factories.value_objects import create_account_id


@pytest.mark.asyncio
async def test_updates_profile_successfully() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    profile = create_profile(account_id=account_id, username=None)
    command = UpdateProfileCommand(
        first_name="Alice",
        last_name="Smith",
        birth_date=date(1990, 6, 15),
        username="alice_s123",
    )

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = UpdateProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    assert profile.first_name is not None
    assert profile.first_name.value == "Alice"
    assert profile.last_name is not None
    assert profile.last_name.value == "Smith"
    assert profile.birth_date is not None
    assert profile.birth_date.value == date(1990, 6, 15)
    assert profile.username is not None
    assert profile.username.value == "alice_s123"
    cast(AsyncMock, core_unit_of_work.commit).assert_awaited_once()
    cast(AsyncMock, event_dispatcher.dispatch).assert_awaited_once()


@pytest.mark.asyncio
async def test_clears_fields_with_null() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    profile = create_profile(account_id=account_id, username=None)
    command = UpdateProfileCommand(
        first_name=None,
        last_name=None,
        birth_date=None,
        username=None,
    )

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = UpdateProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    assert profile.first_name is None
    assert profile.last_name is None
    assert profile.birth_date is None
    assert profile.username is None


@pytest.mark.asyncio
async def test_profile_not_found_raises_error() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    command = UpdateProfileCommand(
        first_name="Alice",
        last_name=None,
        birth_date=None,
        username=None,
    )

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = None

    sut = UpdateProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(ProfileNotFoundByAccountIdError):
        await sut.execute(command)


@pytest.mark.asyncio
async def test_domain_error_on_invalid_username() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    profile = create_profile(account_id=account_id, username=None)
    command = UpdateProfileCommand(
        first_name=None,
        last_name=None,
        birth_date=None,
        username="x",  # too short
    )

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = UpdateProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(DomainTypeError):
        await sut.execute(command)

    cast(AsyncMock, core_unit_of_work.commit).assert_not_awaited()
