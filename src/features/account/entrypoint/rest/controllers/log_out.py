from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from common.adapter.exceptions.gateway import DataMapperError
from features.account.domain.port.inbound.log_out_use_case import LogOutUseCase
from features.account.entrypoint.exceptions.authorization import AuthorizationError

from features.account.entrypoint.rest.openapi_marker import cookie_scheme
from common.entrypoint.rest.errors.callbacks import (
    log_error,
    log_info,
)
from common.entrypoint.rest.errors.translators import (
    ServiceUnavailableTranslator,
)
from features.user.adapter.exceptions.exceptions import AuthenticationError


def create_log_out_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/logout",
        description=getdoc(LogOutUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
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
