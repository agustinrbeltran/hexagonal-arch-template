from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from account.application.refresh_token.command import RefreshTokenCommand
from account.application.refresh_token.handler import RefreshTokenHandler
from account.application.shared.token_pair_refresher import TokenPairRefresher


@pytest.mark.asyncio
async def test_refresh_token_returns_new_token_pair() -> None:
    token_pair_refresher = create_autospec(TokenPairRefresher, instance=True)

    command = RefreshTokenCommand(refresh_token="r1")
    cast(AsyncMock, token_pair_refresher.refresh).return_value = (
        "access",
        "new-refresh",
    )
    token_pair_refresher.access_token_expiry_seconds = 300

    sut = RefreshTokenHandler(
        token_pair_refresher=cast(TokenPairRefresher, token_pair_refresher),
    )

    result = await sut.execute(command)

    assert result.access_token == "access"  # noqa: S105
    assert result.refresh_token == "new-refresh"  # noqa: S105
    assert result.expires_in == 300
    cast(AsyncMock, token_pair_refresher.refresh).assert_awaited_once()
