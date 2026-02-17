from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from application.refresh_token.command import RefreshTokenCommand
from application.refresh_token.handler import RefreshTokenHandler
from application.shared.auth_unit_of_work import AuthUnitOfWork
from application.shared.token_pair_refresher import TokenPairRefresher


@pytest.mark.asyncio
async def test_refresh_token_commits_auth_uow_after_rotation() -> None:
    token_pair_refresher = create_autospec(TokenPairRefresher, instance=True)
    auth_unit_of_work = create_autospec(AuthUnitOfWork, instance=True)

    command = RefreshTokenCommand(refresh_token="r1")
    cast(AsyncMock, token_pair_refresher.refresh).return_value = (
        "access",
        "new-refresh",
    )
    token_pair_refresher.access_token_expiry_seconds = 300
    cast(AsyncMock, auth_unit_of_work.commit).return_value = None

    sut = RefreshTokenHandler(
        token_pair_refresher=cast(TokenPairRefresher, token_pair_refresher),
        auth_unit_of_work=cast(AuthUnitOfWork, auth_unit_of_work),
    )

    result = await sut.execute(command)

    assert result.access_token == "access"  # noqa: S105
    assert result.refresh_token == "new-refresh"  # noqa: S105
    assert result.expires_in == 300
    cast(AsyncMock, auth_unit_of_work.commit).assert_awaited_once()
