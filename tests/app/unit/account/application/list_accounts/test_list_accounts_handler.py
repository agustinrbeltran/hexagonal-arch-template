from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from account.application.current_account.handler import CurrentAccountHandler
from account.application.list_accounts.handler import ListAccountsHandler
from account.application.list_accounts.query import ListAccountsQuery
from account.domain.account.enums import AccountRole
from account.domain.account.repository import AccountRepository, ListAccountsQM
from shared.domain.errors import AuthorizationError
from shared.domain.queries import SortingOrder
from tests.app.unit.factories.account_entity import create_account


@pytest.mark.asyncio
async def test_returns_repo_result() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)

    admin = create_account(role=AccountRole.ADMIN)
    expected: ListAccountsQM = {"accounts": [], "total": 0}
    query = ListAccountsQuery(
        limit=10, offset=0, sorting_field="email", sorting_order=SortingOrder.ASC
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = admin
    cast(AsyncMock, account_repository.get_all).return_value = expected

    sut = ListAccountsHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_repository=cast(AccountRepository, account_repository),
    )

    result = await sut.execute(query)

    assert result == expected
    cast(AsyncMock, account_repository.get_all).assert_awaited_once()


@pytest.mark.asyncio
async def test_user_caller_raises_authorization_error() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)

    user = create_account(role=AccountRole.USER)
    query = ListAccountsQuery(
        limit=10, offset=0, sorting_field="email", sorting_order=SortingOrder.ASC
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = user

    sut = ListAccountsHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_repository=cast(AccountRepository, account_repository),
    )

    with pytest.raises(AuthorizationError):
        await sut.execute(query)


@pytest.mark.asyncio
async def test_pagination_and_sorting_forwarded_to_repo() -> None:
    current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)

    admin = create_account(role=AccountRole.ADMIN)
    expected: ListAccountsQM = {"accounts": [], "total": 0}
    query = ListAccountsQuery(
        limit=25, offset=50, sorting_field="role", sorting_order=SortingOrder.DESC
    )

    cast(AsyncMock, current_account_handler.get_current_account).return_value = admin
    cast(AsyncMock, account_repository.get_all).return_value = expected

    sut = ListAccountsHandler(
        current_account_handler=cast(CurrentAccountHandler, current_account_handler),
        account_repository=cast(AccountRepository, account_repository),
    )

    await sut.execute(query)

    call_args = cast(AsyncMock, account_repository.get_all).call_args
    assert call_args.kwargs["pagination"].limit == 25
    assert call_args.kwargs["pagination"].offset == 50
    assert call_args.kwargs["sorting"].field == "role"
    assert call_args.kwargs["sorting"].order == SortingOrder.DESC
