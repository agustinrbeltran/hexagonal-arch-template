import logging

from account.application.refresh_token.command import (
    RefreshTokenCommand,
    RefreshTokenResult,
)
from account.application.refresh_token.port import RefreshTokenUseCase
from account.application.shared.auth_unit_of_work import AuthUnitOfWork
from account.application.shared.token_pair_refresher import TokenPairRefresher

log = logging.getLogger(__name__)


class RefreshTokenHandler(RefreshTokenUseCase):
    def __init__(
        self,
        token_pair_refresher: TokenPairRefresher,
        auth_unit_of_work: AuthUnitOfWork,
    ) -> None:
        self._token_pair_refresher = token_pair_refresher
        self._auth_unit_of_work = auth_unit_of_work

    async def execute(self, command: RefreshTokenCommand) -> RefreshTokenResult:
        """:raises RefreshTokenNotFoundError, RefreshTokenExpiredError:"""
        log.info("Refresh token: started.")

        access_token, refresh_token = await self._token_pair_refresher.refresh(
            command.refresh_token,
        )
        await self._auth_unit_of_work.commit()

        log.info("Refresh token: done.")

        return RefreshTokenResult(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._token_pair_refresher.access_token_expiry_seconds,
        )
