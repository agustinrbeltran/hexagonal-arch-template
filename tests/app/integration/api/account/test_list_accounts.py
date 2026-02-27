from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest

from account.domain.account.enums import AccountRole
from account.domain.account.repository import AccountQueryModel, ListAccountsQM
from shared.domain.account_id import AccountId
from tests.app.integration.conftest import FakeIdentityProvider
from tests.app.unit.factories.account_entity import create_account


class TestListAccounts:
    @pytest.mark.asyncio
    async def test_default_pagination_returns_200(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        fake_identity: FakeIdentityProvider,
        mock_account_repo: AsyncMock,
        account_id: AccountId,
    ) -> None:
        fake_identity.set_current_account(account_id)
        admin = create_account(
            account_id=account_id, role=AccountRole.ADMIN, is_active=True
        )
        mock_account_repo.get_by_id.return_value = admin
        mock_account_repo.get_all.return_value = ListAccountsQM(
            accounts=[
                AccountQueryModel(
                    id_=uuid4(),
                    email="a@example.com",
                    role=AccountRole.USER,
                    is_active=True,
                ),
            ],
            total=1,
        )

        response = await client.get("/api/v1/accounts/", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert "accounts" in body
        assert body["total"] == 1

    @pytest.mark.asyncio
    async def test_custom_pagination_forwarded(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        fake_identity: FakeIdentityProvider,
        mock_account_repo: AsyncMock,
        account_id: AccountId,
    ) -> None:
        fake_identity.set_current_account(account_id)
        admin = create_account(
            account_id=account_id, role=AccountRole.ADMIN, is_active=True
        )
        mock_account_repo.get_by_id.return_value = admin
        mock_account_repo.get_all.return_value = ListAccountsQM(accounts=[], total=0)

        response = await client.get(
            "/api/v1/accounts/?limit=5&offset=10",
            headers=auth_headers,
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_403(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/accounts/")

        assert response.status_code == 403
