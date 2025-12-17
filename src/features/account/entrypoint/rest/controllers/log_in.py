from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter, rule

from common.adapter.exceptions.gateway import DataMapperError
from common.domain.core.exceptions.base import DomainTypeError
from features.account.domain.port.inbound.log_in_use_case import LogInUseCase, \
  LogInCommand
from features.account.entrypoint.exceptions.authorization import AuthorizationError

from common.entrypoint.rest.errors.callbacks import log_error, log_info
from common.entrypoint.rest.errors.translators import (
    ServiceUnavailableTranslator,
)
from features.user.adapter.exceptions.exceptions import \
  AlreadyAuthenticatedError, AuthenticationError
from features.user.adapter.exceptions.password_hasher import \
  PasswordHasherBusyError
from features.user.domain.core.exceptions.user import \
  UserNotFoundByUsernameError


def create_log_in_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/login",
        description=getdoc(LogInUseCase),
        error_map={
            AlreadyAuthenticatedError: status.HTTP_403_FORBIDDEN,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            UserNotFoundByUsernameError: status.HTTP_404_NOT_FOUND,
            PasswordHasherBusyError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def login(
        request_data: LogInCommand,
        handler: FromDishka[LogInUseCase],
    ) -> None:
        await handler.execute(request_data)

    return router
