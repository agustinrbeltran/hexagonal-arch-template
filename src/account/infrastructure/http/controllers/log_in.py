from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter, rule

from account.application.log_in.command import LogInCommand
from account.application.log_in.handler import AuthenticationError
from account.application.log_in.port import LogInUseCase
from account.domain.account.errors import AccountNotFoundByEmailError
from account.infrastructure.http.schemas.token_response import TokenResponse
from shared.domain.errors import DomainTypeError
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.persistence.errors import DataMapperError


def create_log_in_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/login",
        description=getdoc(LogInUseCase),
        error_map={
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            AccountNotFoundByEmailError: status.HTTP_404_NOT_FOUND,
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        response_model=TokenResponse,
    )
    @inject
    async def login(
        request_data: LogInCommand,
        handler: FromDishka[LogInUseCase],
    ) -> TokenResponse:
        result = await handler.execute(request_data)
        return TokenResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            expires_in=result.expires_in,
        )

    return router
