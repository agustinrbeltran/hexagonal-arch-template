from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from application.list_users.port import ListUsersUseCase
from application.list_users.query import ListUsersQuery
from domain.shared.errors import AuthorizationError
from domain.shared.queries import PaginationError, SortingError, SortingOrder
from domain.user.repository import ListUsersQM
from domain.auth_session.errors import SessionNotFoundError
from infrastructure.http.errors.callbacks import log_error, log_info
from infrastructure.http.errors.translators import ServiceUnavailableTranslator
from infrastructure.http.middleware.openapi_marker import cookie_scheme
from infrastructure.persistence.errors import DataMapperError, ReaderError


class ListUsersRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)
    limit: Annotated[int, Field(ge=1)] = 20
    offset: Annotated[int, Field(ge=0)] = 0
    sorting_field: Annotated[str, Field()] = "username"
    sorting_order: Annotated[SortingOrder, Field()] = SortingOrder.ASC


def create_list_users_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/",
        description=getdoc(ListUsersUseCase),
        error_map={
            SessionNotFoundError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
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
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def list_users(
        request_data_pydantic: Annotated[ListUsersRequestPydantic, Depends()],
        use_case: FromDishka[ListUsersUseCase],
    ) -> ListUsersQM:
        request_data = ListUsersQuery(
            limit=request_data_pydantic.limit,
            offset=request_data_pydantic.offset,
            sorting_field=request_data_pydantic.sorting_field,
            sorting_order=request_data_pydantic.sorting_order,
        )
        return await use_case.execute(request_data)

    return router
