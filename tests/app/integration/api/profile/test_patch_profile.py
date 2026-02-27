from unittest.mock import AsyncMock

import httpx
import pytest

from shared.domain.account_id import AccountId
from tests.app.integration.conftest import FakeIdentityProvider
from tests.app.unit.factories.profile_entity import create_profile


class TestPatchProfile:
    @pytest.mark.asyncio
    async def test_authenticated_patch_returns_204(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        fake_identity: FakeIdentityProvider,
        mock_profile_repo: AsyncMock,
        account_id: AccountId,
    ) -> None:
        fake_identity.set_current_account(account_id)
        profile = create_profile(account_id=account_id)
        mock_profile_repo.get_by_account_id.return_value = profile

        response = await client.patch(
            "/api/v1/profiles/me",
            json={"first_name": "Bob"},
            headers=auth_headers,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_403(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.patch(
            "/api/v1/profiles/me",
            json={"first_name": "Bob"},
        )

        assert response.status_code == 403
