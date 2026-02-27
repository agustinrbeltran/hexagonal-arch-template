from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest

from account.domain.account.enums import AccountRole
from shared.domain.account_id import AccountId
from tests.app.integration.conftest import FakeIdentityProvider
from tests.app.unit.factories.account_entity import create_account


class TestCreateAccount:
    @pytest.mark.asyncio
    async def test_admin_creates_returns_201(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        fake_identity: FakeIdentityProvider,
        mock_account_repo: AsyncMock,
        mock_account_provisioner: AsyncMock,
        account_id: AccountId,
    ) -> None:
        fake_identity.set_current_account(account_id)
        admin = create_account(
            account_id=account_id, role=AccountRole.ADMIN, is_active=True
        )
        mock_account_repo.get_by_id.return_value = admin
        new_id = uuid4()
        mock_account_provisioner.register.return_value = AccountId(new_id)

        response = await client.post(
            "/api/v1/accounts/",
            json={
                "email": "admin-created@example.com",
                "password": "Strong Pass 1",
                "role": "user",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["id"] == str(new_id)

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_403(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/api/v1/accounts/",
            json={
                "email": "new@example.com",
                "password": "Strong Pass 1",
                "role": "user",
            },
        )

        assert response.status_code == 403
