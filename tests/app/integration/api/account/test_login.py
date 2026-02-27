from unittest.mock import AsyncMock

import httpx
import pytest

from account.application.log_in.handler import AuthenticationError
from account.domain.account.enums import AccountRole
from tests.app.unit.factories.account_entity import create_account


class TestLogIn:
    @pytest.mark.asyncio
    async def test_successful_login_returns_200_with_tokens(
        self,
        client: httpx.AsyncClient,
        mock_account_repo: AsyncMock,
        mock_token_pair_issuer: AsyncMock,
    ) -> None:
        account = create_account(role=AccountRole.USER, is_active=True)
        mock_account_repo.get_by_email.return_value = account
        mock_token_pair_issuer.issue_token_pair.return_value = (
            "access-tok",
            "refresh-tok",
        )
        mock_token_pair_issuer.access_token_expiry_seconds = 300

        response = await client.post(
            "/api/v1/accounts/login",
            json={"email": account.email.value, "password": "Strong Pass 1"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"] == "access-tok"  # noqa: S105
        assert body["refresh_token"] == "refresh-tok"  # noqa: S105
        assert body["token_type"] == "bearer"  # noqa: S105
        assert body["expires_in"] == 300

    @pytest.mark.asyncio
    async def test_invalid_credentials_returns_401(
        self,
        client: httpx.AsyncClient,
        mock_account_repo: AsyncMock,
        mock_token_pair_issuer: AsyncMock,
    ) -> None:
        account = create_account(role=AccountRole.USER, is_active=True)
        mock_account_repo.get_by_email.return_value = account
        mock_token_pair_issuer.issue_token_pair.side_effect = AuthenticationError(
            "Bad creds"
        )

        response = await client.post(
            "/api/v1/accounts/login",
            json={"email": account.email.value, "password": "Wrong Pass"},
        )

        assert response.status_code == 401
