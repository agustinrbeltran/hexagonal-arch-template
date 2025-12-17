import asyncio
import logging
from collections.abc import AsyncIterator, Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import cast

from dishka import Provider, Scope, provide, provide_all
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from common.adapter.types_ import (
    HasherSemaphore,
    HasherThreadPoolExecutor,
    MainAsyncSession,
)
from features.account.adapter.sqla_auth_session_gateway_session_adapter import (
    SqlaAuthSessionGatewayAdapter,
)
from features.account.adapter.sqla_auth_session_transaction_manager import (
    SqlaAuthSessionTransactionManager,
)
from features.account.adapter.types_ import AuthAsyncSession
from features.account.domain.core.services.auth_session_service import (
    AuthSessionService,
)
from features.account.domain.port.inbound.change_password_use_case import (
    ChangePasswordUseCase,
)
from features.account.domain.port.inbound.log_in_use_case import LogInUseCase
from features.account.domain.port.inbound.log_out_use_case import LogOutUseCase
from features.account.domain.port.inbound.sign_up_use_case import SignUpUseCase
from features.account.domain.port.outbound.auth_session_gateway import (
    AuthSessionGateway,
)
from features.account.domain.port.outbound.auth_session_transaction_manager import (
    AuthSessionTransactionManager,
)
from features.account.domain.port.outbound.auth_session_transport import (
    AuthSessionTransport,
)
from features.account.entrypoint.rest.session_transport_jwt_cookie import (
    JwtCookieAuthSessionTransport,
)
from features.user.adapter.utils.id_generator_str import (
    StrAuthSessionIdGenerator,
)
from features.user.adapter.utils.timer_utc import UtcAuthSessionTimer
from setup.config.database import PostgresSettings, SqlaEngineSettings
from setup.config.security import SecuritySettings

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


class AuthSessionProvider(Provider):
    scope = Scope.REQUEST

    service = provide(AuthSessionService)

    # Ports
    id_generator = provide(StrAuthSessionIdGenerator, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def provide_utc_auth_session_timer(
        self,
        security: SecuritySettings,
    ) -> UtcAuthSessionTimer:
        return UtcAuthSessionTimer(
            ttl_min=security.auth.session_ttl_min,
            refresh_threshold=security.auth.session_refresh_threshold,
        )

    gateway = provide(SqlaAuthSessionGatewayAdapter, provides=AuthSessionGateway)
    transport = provide(JwtCookieAuthSessionTransport, provides=AuthSessionTransport)
    tx_manager = provide(
        SqlaAuthSessionTransactionManager,
        provides=AuthSessionTransactionManager,
    )


class AuthHandlersProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        SignUpUseCase,
        LogInUseCase,
        ChangePasswordUseCase,
        LogOutUseCase,
    )


def infrastructure_providers() -> tuple[Provider, ...]:
    return (
        MainAdaptersProvider(),
        PersistenceSqlaProvider(),
        AuthSessionProvider(),
        AuthHandlersProvider(),
    )
