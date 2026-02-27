from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest

from account.domain.account.errors import EmailAlreadyExistsError
from account.domain.account.value_objects import Email
from shared.domain.account_id import AccountId


class TestSignUp:
    @pytest.mark.asyncio
    async def test_successful_signup_returns_201(
        self,
        client: httpx.AsyncClient,
        mock_account_provisioner: AsyncMock,
    ) -> None:
        new_id = uuid4()
        mock_account_provisioner.register.return_value = AccountId(new_id)

        response = await client.post(
            "/api/v1/accounts/signup",
            json={"email": "new@example.com", "password": "Strong Pass 1"},
        )

        assert response.status_code == 201
        assert response.json()["id"] == str(new_id)

    @pytest.mark.asyncio
    async def test_duplicate_email_returns_409(
        self,
        client: httpx.AsyncClient,
        mock_account_provisioner: AsyncMock,
    ) -> None:
        mock_account_provisioner.register.side_effect = EmailAlreadyExistsError(
            Email("dup@example.com"),
        )

        response = await client.post(
            "/api/v1/accounts/signup",
            json={"email": "dup@example.com", "password": "Strong Pass 1"},
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_invalid_email_returns_400(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.post(
            "/api/v1/accounts/signup",
            json={"email": "not-an-email", "password": "Strong Pass 1"},
        )

        assert response.status_code == 400
