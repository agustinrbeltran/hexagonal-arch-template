from typing import cast
from unittest.mock import AsyncMock, create_autospec
from uuid import uuid4

import pytest

from account.domain.account.enums import AccountRole
from account.domain.account.events import AccountCreated
from core.application.create_profile.command import CreateProfileCommand
from core.application.create_profile.port import CreateProfileUseCase
from core.infrastructure.events.handlers.create_profile_on_account_created import (
    CreateProfileOnAccountCreated,
)


@pytest.mark.asyncio
async def test_delegates_to_create_profile_use_case() -> None:
    create_profile = create_autospec(CreateProfileUseCase, instance=True)
    account_id = uuid4()

    event = AccountCreated(
        account_id=account_id,
        email="alice@example.com",
        role=AccountRole.USER,
    )

    sut = CreateProfileOnAccountCreated(
        create_profile=cast(CreateProfileUseCase, create_profile),
    )

    await sut.handle(event)

    cast(AsyncMock, create_profile.execute).assert_awaited_once_with(
        CreateProfileCommand(account_id=account_id),
    )
