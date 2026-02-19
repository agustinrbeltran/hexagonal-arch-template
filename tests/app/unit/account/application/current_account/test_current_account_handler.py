from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from account.application.current_account.handler import CurrentAccountHandler
from account.domain.account.ports import AccessRevoker
from account.domain.account.repository import AccountRepository
from shared.domain.errors import AuthorizationError
from shared.domain.ports.identity_provider import IdentityProvider
from tests.app.unit.factories.account_entity import create_account
from tests.app.unit.factories.value_objects import create_account_id


@pytest.mark.asyncio
async def test_returns_active_account() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    access_revoker = create_autospec(AccessRevoker, instance=True)

    account_id = create_account_id()
    account = create_account(account_id=account_id, is_active=True)
    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, account_repository.get_by_id).return_value = account

    sut = CurrentAccountHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        account_repository=cast(AccountRepository, account_repository),
        access_revoker=cast(AccessRevoker, access_revoker),
    )

    result = await sut.get_current_account()

    assert result == account
    cast(AsyncMock, access_revoker.remove_all_account_access).assert_not_awaited()


@pytest.mark.asyncio
async def test_raises_and_revokes_when_account_is_none() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    access_revoker = create_autospec(AccessRevoker, instance=True)

    account_id = create_account_id()
    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, account_repository.get_by_id).return_value = None

    sut = CurrentAccountHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        account_repository=cast(AccountRepository, account_repository),
        access_revoker=cast(AccessRevoker, access_revoker),
    )

    with pytest.raises(AuthorizationError):
        await sut.get_current_account()

    cast(AsyncMock, access_revoker.remove_all_account_access).assert_awaited_once_with(
        account_id,
    )


@pytest.mark.asyncio
async def test_raises_and_revokes_when_account_is_inactive() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    access_revoker = create_autospec(AccessRevoker, instance=True)

    account_id = create_account_id()
    account = create_account(account_id=account_id, is_active=False)
    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, account_repository.get_by_id).return_value = account

    sut = CurrentAccountHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        account_repository=cast(AccountRepository, account_repository),
        access_revoker=cast(AccessRevoker, access_revoker),
    )

    with pytest.raises(AuthorizationError):
        await sut.get_current_account()

    cast(AsyncMock, access_revoker.remove_all_account_access).assert_awaited_once_with(
        account_id,
    )


@pytest.mark.asyncio
async def test_forwards_for_update_to_repository() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    access_revoker = create_autospec(AccessRevoker, instance=True)

    account_id = create_account_id()
    account = create_account(account_id=account_id, is_active=True)
    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, account_repository.get_by_id).return_value = account

    sut = CurrentAccountHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        account_repository=cast(AccountRepository, account_repository),
        access_revoker=cast(AccessRevoker, access_revoker),
    )

    await sut.get_current_account(for_update=True)

    cast(AsyncMock, account_repository.get_by_id).assert_awaited_once_with(
        account_id,
        for_update=True,
    )
