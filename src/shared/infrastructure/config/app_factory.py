import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.infrastructure.config.di.provider_registry import get_providers
from shared.infrastructure.config.settings.app_settings import AppSettings
from shared.infrastructure.events.registry import auto_discover_handlers
from shared.infrastructure.events.relay import OutboxRelay
from shared.infrastructure.http.routers.root_router import create_root_router

log = logging.getLogger(__name__)


def _map_tables() -> None:
    from account.infrastructure.persistence.mappers.account import (  # noqa: PLC0415
        map_account_metadata_table,
    )
    from core.infrastructure.persistence.mappers.profile import (  # noqa: PLC0415
        map_profiles_table,
    )
    from shared.infrastructure.persistence.mappers.outbox import (  # noqa: PLC0415
        map_outbox_table,
    )

    map_account_metadata_table()
    map_profiles_table()
    map_outbox_table()


def create_ioc_container(
    settings: AppSettings,
    *di_providers: Provider,
) -> AsyncContainer:
    return make_async_container(
        *get_providers(),
        *di_providers,
        context={AppSettings: settings},
    )


def create_web_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )
    app.include_router(create_root_router())
    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _map_tables()
    auto_discover_handlers()

    container: AsyncContainer = app.state.dishka_container
    session_factory = await container.get(async_sessionmaker[AsyncSession])

    relay = OutboxRelay(container=container, session_factory=session_factory)
    relay_task = asyncio.create_task(relay.run())

    yield

    relay_task.cancel()
    try:
        await relay_task
    except asyncio.CancelledError:
        log.debug("Outbox relay task cancelled.")

    # https://dishka.readthedocs.io/en/stable/integrations/fastapi.html
    await container.close()
