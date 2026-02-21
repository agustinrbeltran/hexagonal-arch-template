from datetime import date
from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from core.application.patch_profile.command import PatchProfileCommand
from core.application.patch_profile.handler import PatchProfileHandler
from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from core.domain.profile.repository import ProfileRepository
from core.domain.profile.value_objects import BirthDate, FirstName, LastName
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.ports.identity_provider import IdentityProvider
from tests.app.unit.factories.profile_entity import create_profile
from tests.app.unit.factories.value_objects import create_account_id, create_username


@pytest.mark.asyncio
async def test_only_provided_fields_are_updated() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    uname = create_username("alice_s123")
    ln = LastName("Smith")
    bd = BirthDate(date(1990, 6, 15))
    profile = create_profile(
        account_id=account_id, username=uname, last_name=ln, birth_date=bd
    )
    command = PatchProfileCommand(first_name="Andres")

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = PatchProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    assert profile.first_name == FirstName("Andres")
    assert profile.last_name == ln
    assert profile.birth_date == bd
    assert profile.username == uname
    cast(AsyncMock, core_unit_of_work.commit).assert_awaited_once()
    cast(AsyncMock, event_dispatcher.dispatch).assert_awaited_once()


@pytest.mark.asyncio
async def test_explicit_none_clears_field() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    bd = BirthDate(date(1990, 6, 15))
    profile = create_profile(account_id=account_id, username=None, birth_date=bd)
    command = PatchProfileCommand(birth_date=None)

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    sut = PatchProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    assert profile.birth_date is None
    cast(AsyncMock, core_unit_of_work.commit).assert_awaited_once()


@pytest.mark.asyncio
async def test_noop_patch_no_event_but_still_commits() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    fn = FirstName("Alice")
    profile = create_profile(account_id=account_id, username=None, first_name=fn)
    command = PatchProfileCommand(first_name="Alice")

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile

    cast(AsyncMock, event_dispatcher.dispatch).return_value = None

    sut = PatchProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    cast(AsyncMock, core_unit_of_work.commit).assert_awaited_once()
    # dispatch is still called, but with empty list
    cast(AsyncMock, event_dispatcher.dispatch).assert_awaited_once_with([])


@pytest.mark.asyncio
async def test_profile_not_found_raises_error() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    command = PatchProfileCommand(first_name="Andres")

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = None

    sut = PatchProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(ProfileNotFoundByAccountIdError):
        await sut.execute(command)

    cast(AsyncMock, core_unit_of_work.commit).assert_not_awaited()


@pytest.mark.asyncio
async def test_all_unset_command_is_noop() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account_id = create_account_id()
    fn = FirstName("Alice")
    profile = create_profile(account_id=account_id, username=None, first_name=fn)
    command = PatchProfileCommand()  # all UNSET

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, profile_repository.get_by_account_id).return_value = profile
    cast(AsyncMock, event_dispatcher.dispatch).return_value = None

    sut = PatchProfileHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    assert profile.first_name == fn
    cast(AsyncMock, event_dispatcher.dispatch).assert_awaited_once_with([])
