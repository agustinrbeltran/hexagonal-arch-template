from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from application.log_out.port import LogOutUseCase
from domain.auth_session.errors import SessionNotFoundError
from domain.shared.errors import AuthorizationError
from infrastructure.http.errors.callbacks import log_error, log_info
from infrastructure.http.errors.translators import ServiceUnavailableTranslator
from infrastructure.http.middleware.openapi_marker import cookie_scheme
from infrastructure.persistence.errors import DataMapperError


def create_log_out_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/logout",
        description=getdoc(LogOutUseCase),
        error_map={
            SessionNotFoundError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def logout(
        handler: FromDishka[LogOutUseCase],
    ) -> None:
        await handler.execute()

    return router
