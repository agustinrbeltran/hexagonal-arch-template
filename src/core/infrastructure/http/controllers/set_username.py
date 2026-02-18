from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from core.application.set_username.command import SetUsernameCommand
from core.application.set_username.port import SetUsernameUseCase
from core.domain.profile.errors import (
    ProfileNotFoundByAccountIdError,
    UsernameAlreadyExistsError,
)
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.domain.errors import AuthenticationError, DomainTypeError
from shared.infrastructure.persistence.errors import DataMapperError


def create_set_username_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/me/username",
        description=getdoc(SetUsernameUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            ProfileNotFoundByAccountIdError: status.HTTP_404_NOT_FOUND,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
            DataMapperError: rule(
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
    async def set_username(
        username: Annotated[str, Body(embed=True)],
        use_case: FromDishka[SetUsernameUseCase],
    ) -> None:
        command = SetUsernameCommand(username=username)
        await use_case.execute(command)

    return router
