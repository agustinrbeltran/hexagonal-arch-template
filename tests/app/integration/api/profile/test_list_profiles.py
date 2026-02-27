from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest

from core.domain.profile.repository import ListProfilesQM, ProfileQueryModel
from shared.domain.account_id import AccountId
from tests.app.integration.conftest import FakeIdentityProvider


class TestListProfiles:
    @pytest.mark.asyncio
    async def test_default_pagination_returns_200(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        fake_identity: FakeIdentityProvider,
        mock_profile_repo: AsyncMock,
        account_id: AccountId,
    ) -> None:
        fake_identity.set_current_account(account_id)
        mock_profile_repo.get_all.return_value = ListProfilesQM(
            profiles=[
                ProfileQueryModel(
                    id_=uuid4(),
                    account_id=uuid4(),
                    username="alice",
                ),
            ],
            total=1,
        )

        response = await client.get("/api/v1/profiles/", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert "profiles" in body
        assert body["total"] == 1

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_403(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/profiles/")

        assert response.status_code == 403
