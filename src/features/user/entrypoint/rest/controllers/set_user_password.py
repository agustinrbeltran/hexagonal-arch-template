from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from common.adapter.exceptions.gateway import DataMapperError
from common.domain.core.exceptions.base import DomainTypeError
from common.entrypoint.rest.errors.callbacks import log_error, log_info
from common.entrypoint.rest.errors.translators import (
    ServiceUnavailableTranslator,
)
from features.account.entrypoint.exceptions.authorization import AuthorizationError
from features.account.entrypoint.rest.openapi_marker import cookie_scheme
from features.user.adapter.exceptions.exceptions import AuthenticationError
from features.user.adapter.exceptions.password_hasher import PasswordHasherBusyError
from features.user.domain.core.exceptions.user import (
    UserNotFoundByIdError,
)
from features.user.domain.port.inbound.set_user_password_use_case import (
    SetUserPasswordCommand,
    SetUserPasswordUseCase,
)


def create_set_user_password_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{user_id}/password",
        description=getdoc(SetUserPasswordUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            UserNotFoundByIdError: status.HTTP_404_NOT_FOUND,
            PasswordHasherBusyError: rule(
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
    async def set_user_password(
        user_id: Annotated[UUID, Path()],
        password: Annotated[str, Body()],
        interactor: FromDishka[SetUserPasswordUseCase],
    ) -> None:
        request_data = SetUserPasswordCommand(
            user_id=user_id,
            password=password,
        )
        await interactor.execute(request_data)

    return router
