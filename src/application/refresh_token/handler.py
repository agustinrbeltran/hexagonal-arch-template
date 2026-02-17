import logging

from application.refresh_token.command import RefreshTokenCommand, RefreshTokenResult
from application.refresh_token.port import RefreshTokenUseCase
from application.shared.token_pair_refresher import TokenPairRefresher

log = logging.getLogger(__name__)


class RefreshTokenHandler(RefreshTokenUseCase):
    def __init__(
        self,
        token_pair_refresher: TokenPairRefresher,
    ) -> None:
        self._token_pair_refresher = token_pair_refresher

    async def execute(self, command: RefreshTokenCommand) -> RefreshTokenResult:
        """:raises RefreshTokenNotFoundError, RefreshTokenExpiredError:"""
        log.info("Refresh token: started.")

        access_token, refresh_token = await self._token_pair_refresher.refresh(
            command.refresh_token,
        )

        log.info("Refresh token: done.")

        return RefreshTokenResult(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._token_pair_refresher.access_token_expiry_seconds,
        )
