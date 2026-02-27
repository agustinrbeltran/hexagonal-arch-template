from unittest.mock import AsyncMock

import httpx
import pytest


class TestRefreshToken:
    @pytest.mark.asyncio
    async def test_successful_refresh_returns_200_with_new_tokens(
        self,
        client: httpx.AsyncClient,
        mock_token_pair_refresher: AsyncMock,
    ) -> None:
        mock_token_pair_refresher.refresh.return_value = (
            "new-access",
            "new-refresh",
        )
        mock_token_pair_refresher.access_token_expiry_seconds = 300

        response = await client.post(
            "/api/v1/accounts/refresh",
            json={"refresh_token": "old-refresh-tok"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"] == "new-access"  # noqa: S105
        assert body["refresh_token"] == "new-refresh"  # noqa: S105
        assert body["expires_in"] == 300
