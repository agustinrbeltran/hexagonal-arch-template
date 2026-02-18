from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from config.di.provider_registry import get_providers
from config.settings.app_settings import AppSettings
from shared.infrastructure.http.routers.root_router import create_root_router
from shared.infrastructure.events.registry import auto_discover_handlers


def _map_tables() -> None:
    from account.infrastructure.persistence.mappers.account import map_accounts_table
    from account.infrastructure.persistence.mappers.refresh_token import (
        map_refresh_tokens_table,
    )
    from core.infrastructure.persistence.mappers.profile import map_profiles_table

    map_accounts_table()
    map_refresh_tokens_table()
    map_profiles_table()


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
    yield
    # https://dishka.readthedocs.io/en/stable/integrations/fastapi.html
    await app.state.dishka_container.close()
