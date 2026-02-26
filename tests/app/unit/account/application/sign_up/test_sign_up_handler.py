from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from account.application.current_account.handler import CurrentAccountHandler
from account.application.shared.account_provisioner import AccountProvisioner
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.application.sign_up.command import SignUpCommand
from account.application.sign_up.handler import (
    AlreadyAuthenticatedError,
    SignUpHandler,
)
from account.domain.account.errors import EmailAlreadyExistsError
from account.domain.account.repository import AccountRepository
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.errors import AuthorizationError
from tests.app.unit.factories.account_entity import create_account
from tests.app.unit.factories.value_objects import create_account_id


@pytest.mark.asyncio
async def test_signs_up_unauthenticated_user() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_provisioner = create_autospec(AccountProvisioner, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    expected_id = create_account_id()
    command = SignUpCommand(email="new@example.com", password="secret123")

    cast(
        AsyncMock, current_account_handler.get_current_account
    ).side_effect = AuthorizationError("Not authorized.")
    cast(AsyncMock, account_provisioner.register).return_value = expected_id

    sut = SignUpHandler(
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
async def test_already_authenticated_raises_error() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_provisioner = create_autospec(AccountProvisioner, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    existing_account = create_account()
    command = SignUpCommand(email="new@example.com", password="secret123")

    cast(
        AsyncMock, current_account_handler.get_current_account
    ).return_value = existing_account

    sut = SignUpHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_provisioner=cast(AccountProvisioner, account_provisioner),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(AlreadyAuthenticatedError):
        await sut.execute(command)


@pytest.mark.asyncio
async def test_authorization_error_swallowed_and_signup_proceeds() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_provisioner = create_autospec(AccountProvisioner, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    expected_id = create_account_id()
    command = SignUpCommand(email="new@example.com", password="secret123")

    cast(
        AsyncMock, current_account_handler.get_current_account
    ).side_effect = AuthorizationError("Not authorized.")
    cast(AsyncMock, account_provisioner.register).return_value = expected_id

    sut = SignUpHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_provisioner=cast(AccountProvisioner, account_provisioner),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    result = await sut.execute(command)

    assert result["id"] == expected_id.value


@pytest.mark.asyncio
async def test_email_already_exists_propagated() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_provisioner = create_autospec(AccountProvisioner, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    account_unit_of_work = create_autospec(AccountUnitOfWork, instance=True)
    event_dispatcher = create_autospec(EventDispatcher, instance=True)

    expected_id = create_account_id()
    command = SignUpCommand(email="existing@example.com", password="secret123")

    cast(
        AsyncMock, current_account_handler.get_current_account
    ).side_effect = AuthorizationError("Not authorized.")
    cast(AsyncMock, account_provisioner.register).return_value = expected_id
    cast(AsyncMock, account_unit_of_work.commit).side_effect = EmailAlreadyExistsError(
        "existing@example.com"
    )

    sut = SignUpHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_provisioner=cast(AccountProvisioner, account_provisioner),
        account_repository=cast(AccountRepository, account_repository),
        account_unit_of_work=cast(AccountUnitOfWork, account_unit_of_work),
        event_dispatcher=cast(EventDispatcher, event_dispatcher),
    )

    with pytest.raises(EmailAlreadyExistsError):
        await sut.execute(command)
