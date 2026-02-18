from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from account.application.revoke_admin.command import RevokeAdminCommand
from account.application.revoke_admin.port import RevokeAdminUseCase
from account.domain.account.errors import (
    AccountNotFoundByIdError,
    RoleChangeNotPermittedError,
)
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.domain.errors import AuthenticationError, AuthorizationError
from shared.infrastructure.persistence.errors import DataMapperError


def create_revoke_admin_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/{account_id}/roles/admin",
        description=getdoc(RevokeAdminUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            AccountNotFoundByIdError: status.HTTP_404_NOT_FOUND,
            RoleChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(bearer_scheme)],
    )
    @inject
    async def revoke_admin(
        account_id: Annotated[UUID, Path()],
        use_case: FromDishka[RevokeAdminUseCase],
    ) -> None:
        request_data = RevokeAdminCommand(account_id)
        await use_case.execute(request_data)

    return router
