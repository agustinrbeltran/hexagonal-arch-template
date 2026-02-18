from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from account.application.set_account_password.command import SetAccountPasswordCommand
from account.application.set_account_password.port import SetAccountPasswordUseCase
from account.domain.account.errors import AccountNotFoundByIdError
from account.infrastructure.security.errors import PasswordHasherBusyError
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.domain.errors import (
    AuthenticationError,
    AuthorizationError,
    DomainTypeError,
)
from shared.infrastructure.persistence.errors import DataMapperError


def create_set_account_password_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{account_id}/password",
        description=getdoc(SetAccountPasswordUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            AccountNotFoundByIdError: status.HTTP_404_NOT_FOUND,
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
    async def set_account_password(
        account_id: Annotated[UUID, Path()],
        password: Annotated[str, Body()],
        use_case: FromDishka[SetAccountPasswordUseCase],
    ) -> None:
        request_data = SetAccountPasswordCommand(
            account_id=account_id,
            password=password,
        )
        await use_case.execute(request_data)

    return router
