from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from account.application.change_password.command import ChangePasswordCommand
from account.application.change_password.handler import (
    AuthenticationChangeError,
    ChangePasswordHandler,
    ReAuthenticationError,
)
from account.application.current_account.handler import CurrentAccountHandler
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.domain.account.repository import AccountRepository
from account.domain.account.services import AccountService
from shared.application.event_dispatcher import EventDispatcher
from tests.app.unit.factories.account_entity import create_account


@pytest.mark.asyncio
async def test_changes_password_successfully() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_service = create_autospec(AccountService, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account = create_account()
    command = ChangePasswordCommand(
        current_password="old-pass", new_password="new-pass"
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = account
    cast(AsyncMock, account_service.is_password_valid).return_value = True

    sut = ChangePasswordHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_service=cast(AccountService, account_service),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    cast(AsyncMock, account_service.change_password).assert_awaited_once()
    cast(AsyncMock, account_unit_of_work.commit).assert_awaited_once()


@pytest.mark.asyncio
async def test_same_password_raises_authentication_change_error() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_service = create_autospec(AccountService, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account = create_account()
    command = ChangePasswordCommand(
        current_password="same-pass", new_password="same-pass"
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = account

    sut = ChangePasswordHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_service=cast(AccountService, account_service),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(AuthenticationChangeError):
        await sut.execute(command)


@pytest.mark.asyncio
async def test_wrong_current_password_raises_re_authentication_error() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_service = create_autospec(AccountService, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account = create_account()
    command = ChangePasswordCommand(
        current_password="wrong-pass", new_password="new-pass"
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = account
    cast(AsyncMock, account_service.is_password_valid).return_value = False

    sut = ChangePasswordHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_service=cast(AccountService, account_service),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(ReAuthenticationError):
        await sut.execute(command)


@pytest.mark.asyncio
async def test_for_update_forwarded_to_current_account_handler() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_service = create_autospec(AccountService, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    account = create_account()
    command = ChangePasswordCommand(
        current_password="old-pass", new_password="new-pass"
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = account
    cast(AsyncMock, account_service.is_password_valid).return_value = True

    sut = ChangePasswordHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_service=cast(AccountService, account_service),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    cast(
        AsyncMock, current_account_handler.get_current_account
    ).assert_awaited_once_with(for_update=True)
