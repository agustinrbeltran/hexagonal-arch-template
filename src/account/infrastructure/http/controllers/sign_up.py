from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter, rule

from account.application.sign_up.command import SignUpCommand, SignUpResponse
from account.application.sign_up.handler import AlreadyAuthenticatedError
from account.application.sign_up.port import SignUpUseCase
from account.domain.account.errors import (
    EmailAlreadyExistsError,
    RoleAssignmentNotPermittedError,
)
from account.infrastructure.security.errors import PasswordHasherBusyError
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.domain.errors import AuthorizationError, DomainTypeError
from shared.infrastructure.persistence.errors import DataMapperError


def create_sign_up_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/signup",
        description=getdoc(SignUpUseCase),
        error_map={
            AlreadyAuthenticatedError: status.HTTP_403_FORBIDDEN,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            PasswordHasherBusyError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            RoleAssignmentNotPermittedError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            EmailAlreadyExistsError: status.HTTP_409_CONFLICT,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
    )
    @inject
    async def sign_up(
        request_data: SignUpCommand,
        handler: FromDishka[SignUpUseCase],
    ) -> SignUpResponse:
        return await handler.execute(request_data)

    return router
