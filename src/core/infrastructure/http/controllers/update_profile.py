from datetime import date

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from inspect import getdoc
from pydantic import BaseModel

from core.application.update_profile.command import UpdateProfileCommand
from core.application.update_profile.port import UpdateProfileUseCase
from core.domain.profile.errors import (
    ProfileNotFoundByAccountIdError,
    UsernameAlreadyExistsError,
)
from shared.domain.errors import AuthenticationError, DomainTypeError
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.infrastructure.persistence.errors import DataMapperError


class UpdateProfileBody(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    username: str | None = None


_error_map = {
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    ProfileNotFoundByAccountIdError: status.HTTP_404_NOT_FOUND,
    DomainTypeError: status.HTTP_400_BAD_REQUEST,
    UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
    DataMapperError: rule(
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
        translator=ServiceUnavailableTranslator(),
        on_error=log_error,
    ),
}


def create_update_profile_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/me",
        description=getdoc(UpdateProfileUseCase),
        error_map=_error_map,
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(bearer_scheme)],
    )
    @inject
    async def update_profile_put(
        body: UpdateProfileBody,
        use_case: FromDishka[UpdateProfileUseCase],
    ) -> None:
        command = UpdateProfileCommand(
            first_name=body.first_name,
            last_name=body.last_name,
            birth_date=body.birth_date,
            username=body.username,
        )
        await use_case.execute(command)

    @router.patch(
        "/me",
        description=getdoc(UpdateProfileUseCase),
        error_map=_error_map,
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(bearer_scheme)],
    )
    @inject
    async def update_profile_patch(
        body: UpdateProfileBody,
        use_case: FromDishka[UpdateProfileUseCase],
    ) -> None:
        command = UpdateProfileCommand(
            first_name=body.first_name,
            last_name=body.last_name,
            birth_date=body.birth_date,
            username=body.username,
        )
        await use_case.execute(command)

    return router
