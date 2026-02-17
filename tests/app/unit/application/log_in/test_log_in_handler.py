from typing import cast
from unittest.mock import AsyncMock, Mock, create_autospec
from uuid import UUID

import pytest

from application.log_in.command import LogInCommand
from application.log_in.handler import LogInHandler
from application.shared.auth_unit_of_work import AuthUnitOfWork
from application.shared.token_pair_issuer import TokenPairIssuer
from domain.user.entity import User
from domain.user.enums import UserRole
from domain.user.repository import UserRepository
from domain.user.services import UserService
from domain.user.value_objects import UserId, Username, UserPasswordHash


@pytest.mark.asyncio
async def test_login_commits_auth_uow_after_issuing_token_pair() -> None:
    user_repository = create_autospec(UserRepository, instance=True)
    user_service = create_autospec(UserService, instance=True)
    token_pair_issuer = create_autospec(TokenPairIssuer, instance=True)
    auth_unit_of_work = create_autospec(AuthUnitOfWork, instance=True)

    user = User(
        id_=UserId(value=UUID("00000000-0000-0000-0000-000000000001")),
        username=Username("user01"),
        password_hash=UserPasswordHash(b"hash"),
        role=UserRole.USER,
        is_active=True,
    )
    command = LogInCommand(username=user.username.value, password="secret1")
    cast(AsyncMock, user_repository.get_by_username).return_value = user
    cast(AsyncMock, user_service.is_password_valid).return_value = True
    cast(Mock, token_pair_issuer.issue_token_pair).return_value = ("access", "refresh")
    token_pair_issuer.access_token_expiry_seconds = 300
    cast(AsyncMock, auth_unit_of_work.commit).return_value = None

    sut = LogInHandler(
        user_repository=cast(UserRepository, user_repository),
        user_service=cast(UserService, user_service),
        token_pair_issuer=cast(TokenPairIssuer, token_pair_issuer),
        auth_unit_of_work=cast(AuthUnitOfWork, auth_unit_of_work),
    )

    result = await sut.execute(command)

    assert result.access_token == "access"  # noqa: S105
    assert result.refresh_token == "refresh"  # noqa: S105
    assert result.expires_in == 300
    cast(AsyncMock, auth_unit_of_work.commit).assert_awaited_once()
