"""API integration test fixtures.

Contains:
- httpx AsyncClient fixture (task 2.8)
- auth_headers fixture
- Mock accessor fixtures for configuring mock behavior
"""

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from shared.domain.account_id import AccountId
from tests.app.integration.conftest import FakeIdentityProvider, MockRegistry


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def account_id() -> AccountId:
    return AccountId(uuid4())


@pytest.fixture
def _authenticate(
    fake_identity: FakeIdentityProvider,
    account_id: AccountId,
) -> None:
    """Auto-use helper to set up a default authenticated identity."""
    fake_identity.set_current_account(account_id)


# ---------------------------------------------------------------------------
# Convenience mock accessor fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_account_repo(mocks: MockRegistry) -> AsyncMock:
    return mocks.account_repository


@pytest.fixture
def mock_profile_repo(mocks: MockRegistry) -> AsyncMock:
    return mocks.profile_repository


@pytest.fixture
def mock_account_provisioner(mocks: MockRegistry) -> AsyncMock:
    return mocks.account_provisioner


@pytest.fixture
def mock_token_pair_issuer(mocks: MockRegistry) -> AsyncMock:
    return mocks.token_pair_issuer


@pytest.fixture
def mock_token_pair_refresher(mocks: MockRegistry) -> AsyncMock:
    return mocks.token_pair_refresher


@pytest.fixture
def mock_password_resetter(mocks: MockRegistry) -> AsyncMock:
    return mocks.password_resetter


@pytest.fixture
def mock_access_revoker(mocks: MockRegistry) -> AsyncMock:
    return mocks.access_revoker
