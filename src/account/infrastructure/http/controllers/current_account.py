from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from account.application.current_account.port import CurrentAccountUseCase
from account.domain.account.entity import Account
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.http.middleware.openapi_marker import bearer_scheme
from shared.domain.errors import AuthenticationError, AuthorizationError
from shared.infrastructure.persistence.errors import DataMapperError


def create_current_account_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/me",
        description=getdoc(CurrentAccountUseCase),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
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
    async def current_account(
        use_case: FromDishka[CurrentAccountUseCase],
    ) -> dict:
        account: Account = await use_case.get_current_account()
        return {
            "id": account.id_.value,
            "email": account.email.value,
            "role": account.role,
            "is_active": account.is_active,
        }

    return router
