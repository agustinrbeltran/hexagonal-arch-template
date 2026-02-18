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

from account.application.shared.auth_unit_of_work import AuthUnitOfWork
from account.application.shared.token_pair_issuer import TokenPairIssuer
from account.application.shared.token_pair_refresher import TokenPairRefresher
from account.infrastructure.persistence.sqla_auth_unit_of_work import SqlaAuthUnitOfWork
from account.infrastructure.persistence.sqla_refresh_token_repository import (
    SqlaRefreshTokenRepository,
)
from account.infrastructure.security.access_token_processor_jwt import (
    JwtAccessTokenProcessor,
)
from account.infrastructure.security.refresh_token_id_generator import (
    StrRefreshTokenIdGenerator,
)
from account.infrastructure.security.refresh_token_repository import (
    RefreshTokenRepository,
)
from account.infrastructure.security.refresh_token_service import (
    AccessTokenEncoder,
    RefreshTokenIdGenerator,
    RefreshTokenService,
)
from config.settings.database import PostgresSettings, SqlaEngineSettings
from config.settings.security import SecuritySettings
from shared.infrastructure.persistence.types_ import (
    AuthAsyncSession,
    HasherSemaphore,
    HasherThreadPoolExecutor,
    MainAsyncSession,
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


class RefreshTokenProvider(Provider):
    scope = Scope.REQUEST

    # Ports
    auth_unit_of_work = provide(SqlaAuthUnitOfWork, provides=AuthUnitOfWork)
    id_generator = provide(
        StrRefreshTokenIdGenerator, provides=RefreshTokenIdGenerator, scope=Scope.APP
    )
    repository = provide(SqlaRefreshTokenRepository, provides=RefreshTokenRepository)

    @provide
    def provide_access_token_encoder(
        self,
        processor: JwtAccessTokenProcessor,
    ) -> AccessTokenEncoder:
        return processor

    @provide
    def provide_refresh_token_service(
        self,
        repository: RefreshTokenRepository,
        id_generator: RefreshTokenIdGenerator,
        access_token_encoder: AccessTokenEncoder,
        security: SecuritySettings,
    ) -> RefreshTokenService:
        return RefreshTokenService(
            refresh_token_repository=repository,
            refresh_token_id_generator=id_generator,
            access_token_encoder=access_token_encoder,
            access_token_expiry_min=security.auth.access_token_expiry_min,
            refresh_token_expiry_days=security.auth.refresh_token_expiry_days,
        )

    @provide
    def provide_token_pair_issuer(
        self,
        service: RefreshTokenService,
    ) -> TokenPairIssuer:
        return service

    @provide
    def provide_token_pair_refresher(
        self,
        service: RefreshTokenService,
    ) -> TokenPairRefresher:
        return service


def infrastructure_providers() -> tuple[Provider, ...]:
    return (
        MainAdaptersProvider(),
        PersistenceSqlaProvider(),
        RefreshTokenProvider(),
        EntrypointProvider(),
    )
