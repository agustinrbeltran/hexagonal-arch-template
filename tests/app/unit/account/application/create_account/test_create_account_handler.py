from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from account.application.create_account.command import CreateAccountCommand
from account.application.create_account.handler import CreateAccountHandler
from account.application.current_account.handler import CurrentAccountHandler
from account.application.shared.account_provisioner import AccountProvisioner
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.domain.account.enums import AccountRole
from account.domain.account.errors import EmailAlreadyExistsError
from account.domain.account.repository import AccountRepository
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.errors import AuthorizationError
from tests.app.unit.factories.account_entity import create_account
from tests.app.unit.factories.value_objects import create_account_id


@pytest.mark.asyncio
async def test_creates_account_and_returns_response() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_provisioner = create_autospec(AccountProvisioner, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    admin = create_account(role=AccountRole.ADMIN)
    expected_id = create_account_id()
    command = CreateAccountCommand(
        email="new@example.com", password="secret123", role=AccountRole.USER
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = admin
    cast(AsyncMock, account_provisioner.register).return_value = expected_id

    sut = CreateAccountHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_provisioner=cast(AccountProvisioner, account_provisioner),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    result = await sut.execute(command)

    assert result["id"] == expected_id.value
    cast(AsyncMock, account_repository.save).assert_awaited_once()
    cast(AsyncMock, account_unit_of_work.commit).assert_awaited_once()
    cast(AsyncMock, event_dispatcher.dispatch).assert_awaited_once()


@pytest.mark.asyncio
async def test_user_caller_raises_authorization_error() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_provisioner = create_autospec(AccountProvisioner, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    user = create_account(role=AccountRole.USER)
    command = CreateAccountCommand(
        email="new@example.com", password="secret123", role=AccountRole.USER
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = user

    sut = CreateAccountHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_provisioner=cast(AccountProvisioner, account_provisioner),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(AuthorizationError):
        await sut.execute(command)


@pytest.mark.asyncio
async def test_admin_creating_admin_raises_authorization_error() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_provisioner = create_autospec(AccountProvisioner, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    admin = create_account(role=AccountRole.ADMIN)
    command = CreateAccountCommand(
        email="new@example.com", password="secret123", role=AccountRole.ADMIN
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = admin

    sut = CreateAccountHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_provisioner=cast(AccountProvisioner, account_provisioner),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(AuthorizationError):
        await sut.execute(command)


@pytest.mark.asyncio
async def test_email_already_exists_propagated() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_provisioner = create_autospec(AccountProvisioner, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    admin = create_account(role=AccountRole.ADMIN)
    expected_id = create_account_id()
    command = CreateAccountCommand(
        email="existing@example.com", password="secret123", role=AccountRole.USER
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = admin
    cast(AsyncMock, account_provisioner.register).return_value = expected_id
    cast(AsyncMock, account_unit_of_work.commit).side_effect = EmailAlreadyExistsError(
        "existing@example.com"
    )

    sut = CreateAccountHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_provisioner=cast(AccountProvisioner, account_provisioner),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(EmailAlreadyExistsError):
        await sut.execute(command)
