from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from account.application.change_password.command import ChangePasswordCommand
from account.application.change_password.handler import (
    AuthenticationChangeError,
    ReAuthenticationError,
)
from account.application.change_password.port import ChangePasswordUseCase
from account.infrastructure.security.errors import PasswordHasherBusyError
from shared.domain.errors import (
    AuthenticationError,
    AuthorizationError,
    DomainTypeError,
)
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.infrastructure.persistence.errors import DataMapperError


def create_change_password_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/password",
        description=getdoc(ChangePasswordUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            AuthenticationChangeError: status.HTTP_400_BAD_REQUEST,
            ReAuthenticationError: status.HTTP_403_FORBIDDEN,
            PasswordHasherBusyError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(bearer_scheme)],
    )
    @inject
    async def change_password(
        current_password: Annotated[str, Body()],
        new_password: Annotated[str, Body()],
        handler: FromDishka[ChangePasswordUseCase],
    ) -> None:
        request_data = ChangePasswordCommand(
            current_password=current_password,
            new_password=new_password,
        )
        await handler.execute(request_data)

    return router
