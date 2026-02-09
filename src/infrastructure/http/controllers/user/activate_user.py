from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from application.activate_user.command import ActivateUserCommand
from application.activate_user.port import ActivateUserUseCase
from domain.shared.errors import AuthorizationError
from domain.user.errors import ActivationChangeNotPermittedError, UserNotFoundByIdError
from domain.auth_session.errors import SessionNotFoundError
from infrastructure.http.errors.callbacks import log_error, log_info
from infrastructure.http.errors.translators import ServiceUnavailableTranslator
from infrastructure.http.middleware.openapi_marker import cookie_scheme
from infrastructure.persistence.errors import DataMapperError


def create_activate_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{user_id}/activation",
        description=getdoc(ActivateUserUseCase),
        error_map={
            SessionNotFoundError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            UserNotFoundByIdError: status.HTTP_404_NOT_FOUND,
            ActivationChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def activate_user(
        user_id: Annotated[UUID, Path()],
        use_case: FromDishka[ActivateUserUseCase],
    ) -> None:
        request_data = ActivateUserCommand(user_id)
        await use_case.execute(request_data)

    return router
