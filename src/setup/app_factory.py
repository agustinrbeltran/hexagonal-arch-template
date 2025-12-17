from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from common.entrypoint.rest.controllers.root_router import create_root_router
from features.account.entrypoint.rest.asgi_middleware import (
    ASGIAuthMiddleware,
)
from features.user.adapter.mapper.all import map_tables
from setup.config.settings import AppSettings
from setup.ioc.provider_registry import get_providers


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
    # https://github.com/encode/starlette/discussions/2451
    app.add_middleware(ASGIAuthMiddleware)
    # Good place to register global exception handlers
    app.include_router(create_root_router())
    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    map_tables()
    yield
    # https://dishka.readthedocs.io/en/stable/integrations/fastapi.html
    await app.state.dishka_container.close()
