from typing import cast
from unittest.mock import AsyncMock, Mock, create_autospec
from uuid import UUID

import pytest

from account.application.log_in.command import LogInCommand
from account.application.log_in.handler import LogInHandler
from account.application.shared.auth_unit_of_work import AuthUnitOfWork
from account.application.shared.token_pair_issuer import TokenPairIssuer
from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.repository import AccountRepository
from account.domain.account.services import AccountService
from account.domain.account.value_objects import AccountPasswordHash, Email
from shared.domain.account_id import AccountId


@pytest.mark.asyncio
async def test_login_commits_auth_uow_after_issuing_token_pair() -> None:
    account_repository = create_autospec(AccountRepository, instance=True)
    account_service = create_autospec(AccountService, instance=True)
    token_pair_issuer = create_autospec(TokenPairIssuer, instance=True)
    auth_unit_of_work = create_autospec(AuthUnitOfWork, instance=True)

    account = Account(
        id_=AccountId(value=UUID("00000000-0000-0000-0000-000000000001")),
        email=Email("user01@example.com"),
        password_hash=AccountPasswordHash(b"hash"),
        role=AccountRole.USER,
        is_active=True,
    )
    command = LogInCommand(email=account.email.value, password="secret1")
    cast(AsyncMock, account_repository.get_by_email).return_value = account
    cast(AsyncMock, account_service.is_password_valid).return_value = True
    cast(Mock, token_pair_issuer.issue_token_pair).return_value = ("access", "refresh")
    token_pair_issuer.access_token_expiry_seconds = 300
    cast(AsyncMock, auth_unit_of_work.commit).return_value = None

    sut = LogInHandler(
        account_repository=cast(AccountRepository, account_repository),
        account_service=cast(AccountService, account_service),
        token_pair_issuer=cast(TokenPairIssuer, token_pair_issuer),
        auth_unit_of_work=cast(AuthUnitOfWork, auth_unit_of_work),
    )

    result = await sut.execute(command)

    assert result.access_token == "access"  # noqa: S105
    assert result.refresh_token == "refresh"  # noqa: S105
    assert result.expires_in == 300
    cast(AsyncMock, auth_unit_of_work.commit).assert_awaited_once()
