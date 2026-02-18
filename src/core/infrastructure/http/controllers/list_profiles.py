from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from core.application.list_profiles.port import ListProfilesUseCase
from core.application.list_profiles.query import ListProfilesQuery
from core.domain.profile.repository import ListProfilesQM
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.domain.errors import AuthenticationError, AuthorizationError
from shared.domain.queries import PaginationError, SortingError, SortingOrder
from shared.infrastructure.persistence.errors import DataMapperError, ReaderError


class ListProfilesRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)
    limit: Annotated[int, Field(ge=1)] = 20
    offset: Annotated[int, Field(ge=0)] = 0
    sorting_field: Annotated[str, Field()] = "username"
    sorting_order: Annotated[SortingOrder, Field()] = SortingOrder.ASC


def create_list_profiles_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/",
        description=getdoc(ListProfilesUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            PaginationError: status.HTTP_400_BAD_REQUEST,
            SortingError: status.HTTP_400_BAD_REQUEST,
            ReaderError: rule(
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
    async def list_profiles(
        request_data_pydantic: Annotated[ListProfilesRequestPydantic, Depends()],
        use_case: FromDishka[ListProfilesUseCase],
    ) -> ListProfilesQM:
        request_data = ListProfilesQuery(
            limit=request_data_pydantic.limit,
            offset=request_data_pydantic.offset,
            sorting_field=request_data_pydantic.sorting_field,
            sorting_order=request_data_pydantic.sorting_order,
        )
        return await use_case.execute(request_data)

    return router
