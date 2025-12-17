from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter, rule

from common.adapter.exceptions.gateway import DataMapperError
from common.domain.core.exceptions.base import DomainTypeError
from features.account.domain.port.inbound.sign_up_use_case import SignUpUseCase, \
  SignUpCommand, SignUpResponse
from features.account.entrypoint.exceptions.authorization import AuthorizationError

from common.entrypoint.rest.errors.callbacks import (
    log_error,
    log_info,
)
from common.entrypoint.rest.errors.translators import (
    ServiceUnavailableTranslator,
)
from features.user.adapter.exceptions.exceptions import \
  AlreadyAuthenticatedError
from features.user.adapter.exceptions.password_hasher import \
  PasswordHasherBusyError
from features.user.domain.core.exceptions.user import \
  RoleAssignmentNotPermittedError, UsernameAlreadyExistsError


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
            UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
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
