from typing import cast
from unittest.mock import AsyncMock, create_autospec
from uuid import UUID

import pytest

from account.application.log_in.command import LogInCommand
from account.application.log_in.handler import AuthenticationError, LogInHandler
from account.application.shared.token_pair_issuer import TokenPairIssuer
from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.repository import AccountRepository
from account.domain.account.value_objects import Email
from shared.domain.account_id import AccountId


@pytest.mark.asyncio
async def test_login_issues_token_pair_for_active_account() -> None:
    account_repository = create_autospec(AccountRepository, instance=True)
    token_pair_issuer = create_autospec(TokenPairIssuer, instance=True)

    account = Account(
        id_=AccountId(value=UUID("00000000-0000-0000-0000-000000000001")),
        email=Email("user01@example.com"),
        role=AccountRole.USER,
        is_active=True,
    )
    command = LogInCommand(email=account.email.value, password="secret1")
    cast(AsyncMock, account_repository.get_by_email).return_value = account
    cast(AsyncMock, token_pair_issuer.issue_token_pair).return_value = (
        "access",
        "refresh",
    )
    token_pair_issuer.access_token_expiry_seconds = 300

    sut = LogInHandler(
        account_repository=cast(AccountRepository, account_repository),
        token_pair_issuer=cast(TokenPairIssuer, token_pair_issuer),
    )

    result = await sut.execute(command)

    assert result.access_token == "access"  # noqa: S105
    assert result.refresh_token == "refresh"  # noqa: S105
    assert result.expires_in == 300
    cast(AsyncMock, token_pair_issuer.issue_token_pair).assert_awaited_once()


@pytest.mark.asyncio
async def test_login_raises_error_for_inactive_account() -> None:
    account_repository = create_autospec(AccountRepository, instance=True)
    token_pair_issuer = create_autospec(TokenPairIssuer, instance=True)

    account = Account(
        id_=AccountId(value=UUID("00000000-0000-0000-0000-000000000001")),
        email=Email("user01@example.com"),
        role=AccountRole.USER,
        is_active=False,
    )
    command = LogInCommand(email=account.email.value, password="secret1")
    cast(AsyncMock, account_repository.get_by_email).return_value = account

    sut = LogInHandler(
        account_repository=cast(AccountRepository, account_repository),
        token_pair_issuer=cast(TokenPairIssuer, token_pair_issuer),
    )

    with pytest.raises(AuthenticationError):
        await sut.execute(command)
