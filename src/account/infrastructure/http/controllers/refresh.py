from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter, rule

from account.application.refresh_token.command import RefreshTokenCommand
from account.application.refresh_token.port import RefreshTokenUseCase
from account.infrastructure.http.schemas.refresh_request import RefreshRequest
from account.infrastructure.http.schemas.token_response import TokenResponse
from account.infrastructure.security.errors import (
    RefreshTokenExpiredError,
    RefreshTokenNotFoundError,
)
from shared.infrastructure.http.errors.callbacks import log_error, log_info
from shared.infrastructure.http.errors.translators import ServiceUnavailableTranslator
from shared.infrastructure.persistence.errors import DataMapperError


def create_refresh_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/refresh",
        description=getdoc(RefreshTokenUseCase),
        error_map={
            RefreshTokenNotFoundError: status.HTTP_401_UNAUTHORIZED,
            RefreshTokenExpiredError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        response_model=TokenResponse,
    )
    @inject
    async def refresh(
        request_data: RefreshRequest,
        handler: FromDishka[RefreshTokenUseCase],
    ) -> TokenResponse:
        command = RefreshTokenCommand(refresh_token=request_data.refresh_token)
        result = await handler.execute(command)
        return TokenResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            expires_in=result.expires_in,
        )

    return router
