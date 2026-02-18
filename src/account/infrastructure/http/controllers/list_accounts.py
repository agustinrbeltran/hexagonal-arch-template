from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from account.application.list_accounts.port import ListAccountsUseCase
from account.application.list_accounts.query import ListAccountsQuery
from account.domain.account.repository import ListAccountsQM
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.domain.errors import AuthenticationError, AuthorizationError
from shared.domain.queries import PaginationError, SortingError, SortingOrder
from shared.infrastructure.persistence.errors import DataMapperError, ReaderError


class ListAccountsRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)
    limit: Annotated[int, Field(ge=1)] = 20
    offset: Annotated[int, Field(ge=0)] = 0
    sorting_field: Annotated[str, Field()] = "email"
    sorting_order: Annotated[SortingOrder, Field()] = SortingOrder.ASC


def create_list_accounts_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/",
        description=getdoc(ListAccountsUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
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
        dependencies=[Security(bearer_scheme)],
    )
    @inject
    async def list_accounts(
        request_data_pydantic: Annotated[ListAccountsRequestPydantic, Depends()],
        use_case: FromDishka[ListAccountsUseCase],
    ) -> ListAccountsQM:
        request_data = ListAccountsQuery(
            limit=request_data_pydantic.limit,
            offset=request_data_pydantic.offset,
            sorting_field=request_data_pydantic.sorting_field,
            sorting_order=request_data_pydantic.sorting_order,
        )
        return await use_case.execute(request_data)

    return router
