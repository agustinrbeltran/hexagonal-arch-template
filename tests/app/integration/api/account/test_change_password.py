from unittest.mock import AsyncMock

import httpx
import pytest

from shared.domain.account_id import AccountId
from tests.app.integration.conftest import FakeIdentityProvider
from tests.app.unit.factories.account_entity import create_account


class TestChangePassword:
    @pytest.mark.asyncio
    async def test_authenticated_returns_204(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        fake_identity: FakeIdentityProvider,
        mock_account_repo: AsyncMock,
        mock_password_resetter: AsyncMock,
        mock_access_revoker: AsyncMock,
        account_id: AccountId,
    ) -> None:
        fake_identity.set_current_account(account_id)
        account = create_account(account_id=account_id, is_active=True)
        mock_account_repo.get_by_id.return_value = account

        response = await client.put(
            "/api/v1/accounts/password",
            json={"current_password": "Old Pass 1", "new_password": "New Pass 1"},
            headers=auth_headers,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_403(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.put(
            "/api/v1/accounts/password",
            json={"current_password": "Old Pass 1", "new_password": "New Pass 1"},
        )

        assert response.status_code == 403
