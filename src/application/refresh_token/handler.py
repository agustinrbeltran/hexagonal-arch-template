import logging

from application.refresh_token.command import RefreshTokenCommand, RefreshTokenResult
from application.refresh_token.port import RefreshTokenUseCase
from domain.refresh_token.services import RefreshTokenService

log = logging.getLogger(__name__)


class RefreshTokenHandler(RefreshTokenUseCase):
    def __init__(
        self,
        refresh_token_service: RefreshTokenService,
    ) -> None:
        self._refresh_token_service = refresh_token_service

    async def execute(self, command: RefreshTokenCommand) -> RefreshTokenResult:
        """:raises RefreshTokenNotFoundError, RefreshTokenExpiredError:"""
        log.info("Refresh token: started.")

        access_token, refresh_token = await self._refresh_token_service.refresh(
            command.refresh_token,
        )

        log.info("Refresh token: done.")

        return RefreshTokenResult(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._refresh_token_service._access_token_expiry_min * 60,
        )
