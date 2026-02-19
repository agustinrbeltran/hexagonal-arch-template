from typing import cast
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest

from core.application.create_profile.command import CreateProfileCommand
from core.application.create_profile.handler import CreateProfileHandler
from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.domain.profile.entity import Profile
from core.domain.profile.ports import ProfileIdGenerator
from core.domain.profile.repository import ProfileRepository
from tests.app.unit.factories.value_objects import create_account_id, create_profile_id


@pytest.mark.asyncio
async def test_creates_profile_successfully() -> None:
    profile_id_generator = create_autospec(ProfileIdGenerator, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)
    core_unit_of_work = create_autospec(CoreUnitOfWork, instance=True)

    profile_id = create_profile_id()
    account_id = create_account_id()
    command = CreateProfileCommand(account_id=account_id.value)

    cast(MagicMock, profile_id_generator.generate).return_value = profile_id

    sut = CreateProfileHandler(
        profile_id_generator=cast(ProfileIdGenerator, profile_id_generator),
        profile_repository=cast(ProfileRepository, profile_repository),
        core_unit_of_work=cast(CoreUnitOfWork, core_unit_of_work),
    )

    await sut.execute(command)

    cast(MagicMock, profile_repository.save).assert_called_once()
    saved_profile: Profile = cast(MagicMock, profile_repository.save).call_args[0][0]
    assert saved_profile.id_ == profile_id
    assert saved_profile.account_id == account_id
    assert saved_profile.username is None
    cast(AsyncMock, core_unit_of_work.commit).assert_awaited_once()
