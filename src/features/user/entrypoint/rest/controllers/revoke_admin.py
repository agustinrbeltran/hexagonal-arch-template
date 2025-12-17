from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from common.adapter.exceptions.gateway import DataMapperError
from common.entrypoint.rest.errors.callbacks import log_error, log_info
from common.entrypoint.rest.errors.translators import (
    ServiceUnavailableTranslator,
)
from features.account.entrypoint.exceptions.authorization import AuthorizationError
from features.account.entrypoint.rest.openapi_marker import cookie_scheme
from features.user.adapter.exceptions.exceptions import AuthenticationError
from features.user.domain.core.exceptions.user import (
    RoleChangeNotPermittedError,
    UserNotFoundByIdError,
)
from features.user.domain.port.inbound.revoke_admin_use_case import (
    RevokeAdminCommand,
    RevokeAdminUseCase,
)


def create_revoke_admin_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/{user_id}/roles/admin",
        description=getdoc(RevokeAdminUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            UserNotFoundByIdError: status.HTTP_404_NOT_FOUND,
            RoleChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def revoke_admin(
        user_id: Annotated[UUID, Path()],
        interactor: FromDishka[RevokeAdminUseCase],
    ) -> None:
        request_data = RevokeAdminCommand(user_id)
        await interactor.execute(request_data)

    return router
