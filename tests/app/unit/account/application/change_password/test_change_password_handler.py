from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from account.application.change_password.command import ChangePasswordCommand
from account.application.change_password.handler import ChangePasswordHandler
from account.application.current_account.port import CurrentAccountUseCase
from account.application.shared.password_resetter import PasswordResetter
from tests.app.unit.factories.account_entity import create_account


@pytest.mark.asyncio
async def test_changes_password_successfully() -> None:
    current_account_handler = create_autospec(CurrentAccountUseCase, instance=True)
    password_resetter = create_autospec(PasswordResetter, instance=True)

    account = create_account()
    command = ChangePasswordCommand(
        current_password="old-pass", new_password="new-pass"
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = account

    sut = ChangePasswordHandler(
        current_account_handler=cast(CurrentAccountUseCase, current_account_handler),
        password_resetter=cast(PasswordResetter, password_resetter),
    )

    await sut.execute(command)

    cast(AsyncMock, password_resetter.reset_password).assert_awaited_once()


@pytest.mark.asyncio
async def test_get_current_account_called() -> None:
    current_account_handler = create_autospec(CurrentAccountUseCase, instance=True)
    password_resetter = create_autospec(PasswordResetter, instance=True)

    account = create_account()
    command = ChangePasswordCommand(
        current_password="old-pass", new_password="new-pass"
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = account

    sut = ChangePasswordHandler(
        current_account_handler=cast(CurrentAccountUseCase, current_account_handler),
        password_resetter=cast(PasswordResetter, password_resetter),
    )

    await sut.execute(command)

    cast(AsyncMock, current_account_handler.get_current_account).assert_awaited_once()
