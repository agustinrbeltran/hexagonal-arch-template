"""Integration test infrastructure.

Contains:
- FakeIdentityProvider (task 2.1)
- TestSupabaseProvider (task 2.2)
- TestRepositoryProvider (task 2.3)
- TestAuthProvider (task 2.4)
- Test-specific lifespan (task 2.5)
- Programmatic AppSettings (task 2.6)
- Test app factory fixture (task 2.7)
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest
from dishka import Provider, Scope, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from account.application.shared.account_provisioner import AccountProvisioner
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.application.shared.password_resetter import PasswordResetter
from account.application.shared.token_pair_issuer import TokenPairIssuer
from account.application.shared.token_pair_refresher import TokenPairRefresher
from account.domain.account.ports import AccessRevoker
from account.domain.account.repository import AccountRepository
from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.domain.profile.repository import ProfileRepository
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.account_id import AccountId
from shared.domain.errors import AuthenticationError
from shared.domain.ports.authorization_guard import AuthorizationGuard
from shared.domain.ports.identity_provider import IdentityProvider
from shared.infrastructure.config.app_factory import (
    _map_tables,
    create_ioc_container,
)
from shared.infrastructure.config.settings.app_settings import AppSettings
from shared.infrastructure.config.settings.database import (
    PostgresSettings,
    SqlaEngineSettings,
)
from shared.infrastructure.config.settings.logs import LoggingLevel, LoggingSettings
from shared.infrastructure.config.settings.security import (
    AuthSettings,
    SecuritySettings,
    SupabaseSettings,
)
from shared.infrastructure.events.registry import auto_discover_handlers
from shared.infrastructure.http.routers.root_router import create_root_router


# ---------------------------------------------------------------------------
# 2.1  FakeIdentityProvider
# ---------------------------------------------------------------------------
class FakeIdentityProvider(IdentityProvider):
    """Test double that returns a configurable AccountId."""

    def __init__(self) -> None:
        self._current_account_id: AccountId | None = None

    def set_current_account(self, account_id: AccountId) -> None:
        self._current_account_id = account_id

    def clear(self) -> None:
        self._current_account_id = None

    async def get_current_account_id(self) -> AccountId:
        if self._current_account_id is None:
            raise AuthenticationError("No identity configured in test.")
        return self._current_account_id


# ---------------------------------------------------------------------------
# Mock registry — shared mutable state so Provider and tests see same mocks
# ---------------------------------------------------------------------------
class MockRegistry:
    """Holds mock instances that are shared between DI providers and tests."""

    def __init__(self) -> None:
        self.account_provisioner: AsyncMock = cast(
            AsyncMock, create_autospec(AccountProvisioner, instance=True)
        )
        self.password_resetter: AsyncMock = cast(
            AsyncMock, create_autospec(PasswordResetter, instance=True)
        )
        self.token_pair_issuer: AsyncMock = cast(
            AsyncMock, create_autospec(TokenPairIssuer, instance=True)
        )
        self.token_pair_issuer.access_token_expiry_seconds = 300
        self.token_pair_refresher: AsyncMock = cast(
            AsyncMock, create_autospec(TokenPairRefresher, instance=True)
        )
        self.access_revoker: AsyncMock = cast(
            AsyncMock, create_autospec(AccessRevoker, instance=True)
        )
        self.account_repository: AsyncMock = cast(
            AsyncMock, create_autospec(AccountRepository, instance=True)
        )
        self.profile_repository: AsyncMock = cast(
            AsyncMock, create_autospec(ProfileRepository, instance=True)
        )
        self.account_uow: AsyncMock = cast(
            AsyncMock, create_autospec(AccountUnitOfWork, instance=True)
        )
        self.core_uow: AsyncMock = cast(
            AsyncMock, create_autospec(CoreUnitOfWork, instance=True)
        )
        self.event_dispatcher: AsyncMock = cast(
            AsyncMock, create_autospec(EventDispatcher, instance=True)
        )
        self.authorization_guard: AsyncMock = AsyncMock(spec=AuthorizationGuard)
        self.authorization_guard.require_admin = AsyncMock(return_value=None)

    def reset_all(self) -> None:
        for attr in (
            "account_provisioner",
            "password_resetter",
            "token_pair_issuer",
            "token_pair_refresher",
            "access_revoker",
            "account_repository",
            "profile_repository",
            "account_uow",
            "core_uow",
            "event_dispatcher",
            "authorization_guard",
        ):
            mock = getattr(self, attr)
            mock.reset_mock(side_effect=True, return_value=True)
        self.token_pair_issuer.access_token_expiry_seconds = 300
        self.authorization_guard.require_admin = AsyncMock(return_value=None)


_mocks = MockRegistry()
_fake_identity = FakeIdentityProvider()


# ---------------------------------------------------------------------------
# 2.2  TestSupabaseProvider
# ---------------------------------------------------------------------------
class TestSupabaseProvider(Provider):
    """Overrides all Supabase auth adapters with shared mock instances."""

    scope = Scope.APP

    @provide
    def account_provisioner(self) -> AccountProvisioner:
        return cast(AccountProvisioner, _mocks.account_provisioner)

    @provide
    def password_resetter(self) -> PasswordResetter:
        return cast(PasswordResetter, _mocks.password_resetter)

    @provide
    def token_pair_issuer(self) -> TokenPairIssuer:
        return cast(TokenPairIssuer, _mocks.token_pair_issuer)

    @provide
    def token_pair_refresher(self) -> TokenPairRefresher:
        return cast(TokenPairRefresher, _mocks.token_pair_refresher)

    @provide
    def access_revoker(self) -> AccessRevoker:
        return cast(AccessRevoker, _mocks.access_revoker)


# ---------------------------------------------------------------------------
# 2.3  TestRepositoryProvider
# ---------------------------------------------------------------------------
class TestRepositoryProvider(Provider):
    """Overrides repositories, UoWs, and event dispatcher with shared mocks."""

    scope = Scope.REQUEST

    @provide
    def account_repository(self) -> AccountRepository:
        return cast(AccountRepository, _mocks.account_repository)

    @provide
    def profile_repository(self) -> ProfileRepository:
        return cast(ProfileRepository, _mocks.profile_repository)

    @provide
    def account_unit_of_work(self) -> AccountUnitOfWork:
        return cast(AccountUnitOfWork, _mocks.account_uow)

    @provide
    def core_unit_of_work(self) -> CoreUnitOfWork:
        return cast(CoreUnitOfWork, _mocks.core_uow)

    @provide
    def event_dispatcher(self) -> EventDispatcher:
        return cast(EventDispatcher, _mocks.event_dispatcher)


# ---------------------------------------------------------------------------
# 2.4  TestAuthProvider
# ---------------------------------------------------------------------------
class TestAuthProvider(Provider):
    """Provides FakeIdentityProvider and a pass-through AuthorizationGuard."""

    scope = Scope.REQUEST

    @provide
    def identity_provider(self) -> IdentityProvider:
        return _fake_identity

    @provide
    def authorization_guard(self) -> AuthorizationGuard:
        return cast(AuthorizationGuard, _mocks.authorization_guard)


# ---------------------------------------------------------------------------
# 2.5  Test-specific lifespan
# ---------------------------------------------------------------------------
_tables_mapped = False


@asynccontextmanager
async def _test_lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: RUF029, ARG001
    global _tables_mapped  # noqa: PLW0603
    if not _tables_mapped:
        _map_tables()
        _tables_mapped = True
    auto_discover_handlers()
    yield


# ---------------------------------------------------------------------------
# 2.6  Programmatic AppSettings
# ---------------------------------------------------------------------------
def _make_test_settings() -> AppSettings:
    return AppSettings(
        postgres=PostgresSettings(
            **{
                "USER": "test",
                "PASSWORD": "test",
                "DB": "test",
                "HOST": "localhost",
                "PORT": 5432,
                "DRIVER": "psycopg",
            },
        ),
        sqla=SqlaEngineSettings(
            **{
                "ECHO": False,
                "ECHO_POOL": False,
                "POOL_SIZE": 1,
                "MAX_OVERFLOW": 0,
            },
        ),
        security=SecuritySettings(
            auth=AuthSettings(
                **{
                    "JWT_SECRET": "a" * 32,
                    "JWT_ALGORITHM": "HS256",
                    "ACCESS_TOKEN_EXPIRY_MIN": 5,
                },
            ),
            supabase=SupabaseSettings(
                **{
                    "SUPABASE_URL": "http://localhost:54321",
                    "SERVICE_ROLE_KEY": "b" * 32,
                },
            ),
        ),
        logs=LoggingSettings(**{"LEVEL": LoggingLevel.WARNING}),
    )


# ---------------------------------------------------------------------------
# 2.7  Test app factory fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def test_settings() -> AppSettings:
    return _make_test_settings()


@pytest.fixture
def fake_identity() -> FakeIdentityProvider:
    _fake_identity.clear()
    return _fake_identity


@pytest.fixture
def mocks() -> MockRegistry:
    _mocks.reset_all()
    _fake_identity.clear()
    return _mocks


@pytest.fixture
def app(test_settings: AppSettings, mocks: MockRegistry) -> FastAPI:  # noqa: ARG001
    """Create a FastAPI app with test DI overrides."""
    web_app = FastAPI(
        lifespan=_test_lifespan,
        default_response_class=ORJSONResponse,
    )
    web_app.include_router(create_root_router())

    container = create_ioc_container(
        test_settings,
        TestSupabaseProvider(),
        TestRepositoryProvider(),
        TestAuthProvider(),
    )
    setup_dishka(container, web_app)

    return web_app
