from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest

from account.domain.account.enums import AccountRole
from shared.domain.account_id import AccountId
from tests.app.integration.conftest import FakeIdentityProvider
from tests.app.unit.factories.account_entity import create_account


class TestRevokeAdmin:
    @pytest.mark.asyncio
    async def test_authenticated_returns_204(
        self,
        client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        fake_identity: FakeIdentityProvider,
        mock_account_repo: AsyncMock,
        account_id: AccountId,
    ) -> None:
        fake_identity.set_current_account(account_id)
        admin = create_account(
            account_id=account_id, role=AccountRole.SUPER_ADMIN, is_active=True
        )
        target_id = uuid4()
        target = create_account(
            account_id=AccountId(target_id),
            role=AccountRole.ADMIN,
            is_active=True,
        )

        def get_by_id_side_effect(aid: AccountId, for_update: bool = False) -> object:  # noqa: ARG001
            if aid == account_id:
                return admin
            return target

        mock_account_repo.get_by_id.side_effect = get_by_id_side_effect

        response = await client.delete(
            f"/api/v1/accounts/{target_id}/roles/admin",
            headers=auth_headers,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_403(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        target_id = uuid4()

        response = await client.delete(
            f"/api/v1/accounts/{target_id}/roles/admin",
        )

        assert response.status_code == 403
