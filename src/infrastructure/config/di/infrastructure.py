import asyncio
import logging
from collections.abc import AsyncIterator, Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import cast

from dishka import Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.requests import Request

from domain.auth_session.gateway import AuthSessionGateway
from domain.auth_session.ports import (
    AuthSessionTransactionManager,
    AuthSessionTransport,
)
from domain.auth_session.services import (
    AuthSessionIdGenerator,
    AuthSessionService,
    AuthSessionTimer,
)
from infrastructure.config.settings.database import PostgresSettings, SqlaEngineSettings
from infrastructure.config.settings.security import SecuritySettings
from infrastructure.http.middleware.cookie_params import CookieParams
from infrastructure.persistence.sqla_auth_session_gateway import SqlaAuthSessionGateway
from infrastructure.persistence.sqla_auth_session_transaction_manager import (
    SqlaAuthSessionTransactionManager,
)
from infrastructure.persistence.types_ import (
    AuthAsyncSession,
    HasherSemaphore,
    HasherThreadPoolExecutor,
    MainAsyncSession,
)
from infrastructure.security.access_token_processor_jwt import JwtAccessTokenProcessor
from infrastructure.security.auth_session_id_generator import StrAuthSessionIdGenerator
from infrastructure.security.auth_session_timer import UtcAuthSessionTimer
from infrastructure.security.session_transport_jwt_cookie import (
    JwtCookieAuthSessionTransport,
)

log = logging.getLogger(__name__)


class MainAdaptersProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_hasher_threadpool_executor(
        self,
        security: SecuritySettings,
    ) -> Iterator[HasherThreadPoolExecutor]:
        executor = HasherThreadPoolExecutor(
            ThreadPoolExecutor(
                max_workers=security.password.hasher_max_threads,
                thread_name_prefix="bcrypt",
            )
        )
        yield executor
        log.debug("Disposing hasher threadpool executor...")
        executor.shutdown(wait=True, cancel_futures=True)
        log.debug("Hasher threadpool executor is disposed.")

    @provide
    def provide_hasher_semaphore(self, security: SecuritySettings) -> HasherSemaphore:
        return HasherSemaphore(asyncio.Semaphore(security.password.hasher_max_threads))


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

    @provide(scope=Scope.REQUEST)
    async def provide_auth_async_session(
        self,
        async_session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AuthAsyncSession]:
        """Provides UoW (AsyncSession) for the auth context."""
        log.debug("Starting Auth async session...")
        async with async_session_factory() as session:
            log.debug("Auth async session started.")
            yield cast(AuthAsyncSession, session)
            log.debug("Closing Auth async session.")
        log.debug("Auth async session closed.")


class EntrypointProvider(Provider):
    scope = Scope.REQUEST

    request = from_context(provides=Request)

    @provide
    def provide_access_token_processor(
        self,
        security: SecuritySettings,
    ) -> JwtAccessTokenProcessor:
        return JwtAccessTokenProcessor(
            secret=security.auth.jwt_secret,
            algorithm=security.auth.jwt_algorithm,
        )

    @provide
    def provide_cookie_params(self, security: SecuritySettings) -> CookieParams:
        return CookieParams(secure=security.cookies.secure)


class AuthSessionProvider(Provider):
    scope = Scope.REQUEST

    service = provide(AuthSessionService)

    # Ports
    id_generator = provide(
        StrAuthSessionIdGenerator, provides=AuthSessionIdGenerator, scope=Scope.APP
    )

    @provide(scope=Scope.APP)
    def provide_utc_auth_session_timer(
        self,
        security: SecuritySettings,
    ) -> AuthSessionTimer:
        return UtcAuthSessionTimer(
            ttl_min=security.auth.session_ttl_min,
            refresh_threshold=security.auth.session_refresh_threshold,
        )

    gateway = provide(SqlaAuthSessionGateway, provides=AuthSessionGateway)
    transport = provide(JwtCookieAuthSessionTransport, provides=AuthSessionTransport)
    tx_manager = provide(
        SqlaAuthSessionTransactionManager,
        provides=AuthSessionTransactionManager,
    )


def infrastructure_providers() -> tuple[Provider, ...]:
    return (
        MainAdaptersProvider(),
        PersistenceSqlaProvider(),
        AuthSessionProvider(),
        EntrypointProvider(),
    )
