from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter, rule

from application.log_in.command import LogInCommand
from application.log_in.handler import AuthenticationError
from application.log_in.port import LogInUseCase
from application.sign_up.handler import AlreadyAuthenticatedError
from domain.shared.errors import AuthorizationError, DomainTypeError
from domain.user.errors import UserNotFoundByUsernameError
from infrastructure.http.errors.callbacks import log_error, log_info
from infrastructure.http.errors.translators import ServiceUnavailableTranslator
from infrastructure.persistence.errors import DataMapperError
from infrastructure.security.errors import PasswordHasherBusyError


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
