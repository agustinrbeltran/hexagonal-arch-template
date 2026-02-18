from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from core.application.get_my_profile.port import (
    GetMyProfileResponse,
    GetMyProfileUseCase,
)
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.domain.errors import AuthenticationError
from shared.infrastructure.persistence.errors import DataMapperError


def create_get_my_profile_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/me",
        description=getdoc(GetMyProfileUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            ProfileNotFoundByAccountIdError: status.HTTP_404_NOT_FOUND,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        dependencies=[Security(bearer_scheme)],
    )
    @inject
    async def get_my_profile(
        use_case: FromDishka[GetMyProfileUseCase],
    ) -> GetMyProfileResponse:
        return await use_case.execute()

    return router
