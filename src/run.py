from dishka import Provider
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from shared.infrastructure.config.app_factory import (
    create_ioc_container,
    create_web_app,
)
from shared.infrastructure.config.settings.app_settings import (
    AppSettings,
    load_settings,
)
from shared.infrastructure.config.settings.logs import configure_logging


def make_app(
    *di_providers: Provider,
    settings: AppSettings | None = None,
) -> FastAPI:
    """Pass providers to override existing ones for testing."""
    if settings is None:
        configure_logging()
        settings = load_settings()

    configure_logging(level=settings.logs.level)

    app: FastAPI = create_web_app()
    container = create_ioc_container(settings, *di_providers)
    setup_dishka(container, app)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app=make_app(),
        port=8000,
        reload=False,
        loop="uvloop",
    )
