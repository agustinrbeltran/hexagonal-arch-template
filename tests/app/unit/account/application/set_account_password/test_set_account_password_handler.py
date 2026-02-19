from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from account.application.current_account.handler import CurrentAccountHandler
from account.application.set_account_password.command import SetAccountPasswordCommand
from account.application.set_account_password.handler import SetAccountPasswordHandler
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.domain.account.enums import AccountRole
from account.domain.account.errors import AccountNotFoundByIdError
from account.domain.account.repository import AccountRepository
from account.domain.account.services import AccountService
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.errors import AuthorizationError
from tests.app.unit.factories.account_entity import create_account
from tests.app.unit.factories.value_objects import create_account_id


@pytest.mark.asyncio
async def test_sets_password_successfully() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_service = create_autospec(AccountService, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    admin = create_account(role=AccountRole.ADMIN)
    target_id = create_account_id()
    target = create_account(account_id=target_id, role=AccountRole.USER)
    command = SetAccountPasswordCommand(account_id=target_id.value, password="new-pass")

    cast(AsyncMock, current_account_handler.get_current_account).return_value = admin
    cast(AsyncMock, account_repository.get_by_id).return_value = target

    sut = SetAccountPasswordHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_repository=cast(AccountRepository, account_repository),
        account_service=cast(AccountService, account_service),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    await sut.execute(command)

    cast(AsyncMock, account_service.change_password).assert_awaited_once()
    cast(AsyncMock, account_unit_of_work.commit).assert_awaited_once()
    cast(AsyncMock, event_dispatcher.dispatch).assert_awaited_once()


@pytest.mark.asyncio
async def test_user_caller_raises_authorization_error() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_service = create_autospec(AccountService, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    user = create_account(role=AccountRole.USER)
    target_id = create_account_id()
    command = SetAccountPasswordCommand(account_id=target_id.value, password="new-pass")

    cast(AsyncMock, current_account_handler.get_current_account).return_value = user

    sut = SetAccountPasswordHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_repository=cast(AccountRepository, account_repository),
        account_service=cast(AccountService, account_service),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(AuthorizationError):
        await sut.execute(command)


@pytest.mark.asyncio
async def test_target_not_found_raises_error() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_service = create_autospec(AccountService, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    admin = create_account(role=AccountRole.ADMIN)
    target_id = create_account_id()
    command = SetAccountPasswordCommand(account_id=target_id.value, password="new-pass")

    cast(AsyncMock, current_account_handler.get_current_account).return_value = admin
    cast(AsyncMock, account_repository.get_by_id).return_value = None

    sut = SetAccountPasswordHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_repository=cast(AccountRepository, account_repository),
        account_service=cast(AccountService, account_service),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(AccountNotFoundByIdError):
        await sut.execute(command)


@pytest.mark.asyncio
async def test_admin_targeting_admin_raises_authorization_error() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_service = create_autospec(AccountService, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    admin = create_account(role=AccountRole.ADMIN)
    target_id = create_account_id()
    target_admin = create_account(account_id=target_id, role=AccountRole.ADMIN)
    command = SetAccountPasswordCommand(account_id=target_id.value, password="new-pass")

    cast(AsyncMock, current_account_handler.get_current_account).return_value = admin
    cast(AsyncMock, account_repository.get_by_id).return_value = target_admin

    sut = SetAccountPasswordHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_repository=cast(AccountRepository, account_repository),
        account_service=cast(AccountService, account_service),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(AuthorizationError):
        await sut.execute(command)
