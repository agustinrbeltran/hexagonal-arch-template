import logging
from collections.abc import AsyncIterator
from typing import NewType, cast

from dishka import Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.requests import Request

from account.application.shared.account_provisioner import AccountProvisioner
from account.application.shared.password_resetter import PasswordResetter
from account.application.shared.token_pair_issuer import TokenPairIssuer
from account.application.shared.token_pair_refresher import TokenPairRefresher
from account.domain.account.ports import AccessRevoker
from account.infrastructure.security.access_token_processor_jwt import (
    AccessTokenDecoder,
)
from account.infrastructure.security.supabase_auth_adapter import (
    SupabaseAccessRevoker,
    SupabaseAccountProvisioner,
    SupabasePasswordResetter,
    SupabaseTokenPairIssuer,
    SupabaseTokenPairRefresher,
)
from shared.infrastructure.config.settings.database import (
    PostgresSettings,
    SqlaEngineSettings,
)
from shared.infrastructure.config.settings.security import SecuritySettings
from shared.infrastructure.persistence.types_ import MainAsyncSession
from supabase import (
    Client as SupabaseClient,
    create_client,
)

AdminSupabaseClient = NewType("AdminSupabaseClient", SupabaseClient)
AuthSupabaseClient = NewType("AuthSupabaseClient", SupabaseClient)

log = logging.getLogger(__name__)


class PersistenceSqlaProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_async_engine(
        self,
        postgres: PostgresSettings,
        sqla_engine: SqlaEngineSettings,
    ) -> AsyncIterator[AsyncEngine]:
        async_engine = create_async_engine(
            url=postgres.dsn,
            echo=sqla_engine.echo,
            echo_pool=sqla_engine.echo_pool,
            pool_size=sqla_engine.pool_size,
            max_overflow=sqla_engine.max_overflow,
            connect_args={"connect_timeout": 5},
            pool_pre_ping=True,
        )
        log.debug("Async engine created with DSN: %s", postgres.dsn)
        yield async_engine
        log.debug("Disposing async engine...")
        await async_engine.dispose()
        log.debug("Engine is disposed.")

    @provide(scope=Scope.APP)
    def provide_async_session_factory(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        async_session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
        )
        log.debug("Async session maker initialized.")
        return async_session_factory

    @provide(scope=Scope.REQUEST)
    async def provide_main_async_session(
        self,
        async_session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[MainAsyncSession]:
        """Provides UoW (AsyncSession) for the main context."""
        log.debug("Starting Main async session...")
        async with async_session_factory() as session:
            log.debug("Main async session started.")
            yield cast(MainAsyncSession, session)
            log.debug("Closing Main async session.")
        log.debug("Main async session closed.")


class EntrypointProvider(Provider):
    scope = Scope.REQUEST

    request = from_context(provides=Request)

    @provide
    def provide_access_token_decoder(
        self,
        security: SecuritySettings,
    ) -> AccessTokenDecoder:
        jwks_url: str | None = None
        if security.auth.jwt_algorithm.startswith("ES"):
            jwks_url = f"{security.supabase.url}/auth/v1/.well-known/jwks.json"
        return AccessTokenDecoder(
            secret=security.auth.jwt_secret,
            algorithm=security.auth.jwt_algorithm,
            jwks_url=jwks_url,
        )


class SupabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_admin_supabase_client(
        self,
        security: SecuritySettings,
    ) -> AdminSupabaseClient:
        """Dedicated client for admin operations (create_user, etc.).

        Isolated from user auth state changes that would overwrite the
        service-role Authorization header.
        """
        return AdminSupabaseClient(
            create_client(
                security.supabase.url,
                security.supabase.service_role_key,
            )
        )

    @provide(scope=Scope.APP)
    def provide_auth_supabase_client(
        self,
        security: SecuritySettings,
    ) -> AuthSupabaseClient:
        """Dedicated client for user-facing auth (sign_in, refresh)."""
        return AuthSupabaseClient(
            create_client(
                security.supabase.url,
                security.supabase.service_role_key,
            )
        )

    @provide(scope=Scope.APP)
    def provide_account_provisioner(
        self,
        client: AdminSupabaseClient,
    ) -> AccountProvisioner:
        return SupabaseAccountProvisioner(client)

    @provide(scope=Scope.APP)
    def provide_password_resetter(
        self,
        client: AdminSupabaseClient,
    ) -> PasswordResetter:
        return SupabasePasswordResetter(client)

    @provide(scope=Scope.APP)
    def provide_token_pair_issuer(
        self,
        client: AuthSupabaseClient,
        security: SecuritySettings,
    ) -> TokenPairIssuer:
        return SupabaseTokenPairIssuer(
            client=client,
            access_token_expiry_s=security.auth.access_token_expiry_min * 60,
        )

    @provide(scope=Scope.APP)
    def provide_token_pair_refresher(
        self,
        client: AuthSupabaseClient,
        security: SecuritySettings,
    ) -> TokenPairRefresher:
        return SupabaseTokenPairRefresher(
            client=client,
            access_token_expiry_s=security.auth.access_token_expiry_min * 60,
        )

    @provide(scope=Scope.APP)
    def provide_access_revoker(
        self,
        client: AdminSupabaseClient,
    ) -> AccessRevoker:
        return SupabaseAccessRevoker(client)


def infrastructure_providers() -> tuple[Provider, ...]:
    return (
        PersistenceSqlaProvider(),
        EntrypointProvider(),
        SupabaseProvider(),
    )
