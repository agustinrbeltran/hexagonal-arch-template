from unittest.mock import AsyncMock

import httpx
import pytest

from account.domain.account.enums import AccountRole
from shared.domain.account_id import AccountId
from tests.app.integration.conftest import FakeIdentityProvider
from tests.app.unit.factories.account_entity import create_account


class TestCurrentAccount:
    @pytest.mark.asyncio
    async def test_authenticated_returns_200(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        fake_identity: FakeIdentityProvider,
        mock_account_repo: AsyncMock,
        mock_access_revoker: AsyncMock,
        account_id: AccountId,
    ) -> None:
        fake_identity.set_current_account(account_id)
        account = create_account(
            account_id=account_id,
            role=AccountRole.USER,
            is_active=True,
        )
        mock_account_repo.get_by_id.return_value = account

        response = await client.get("/api/v1/accounts/me", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == str(account_id.value)
        assert body["email"] == account.email.value
        assert body["role"] == AccountRole.USER.value
        assert body["is_active"] is True

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_403(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/accounts/me")

        assert response.status_code == 403
