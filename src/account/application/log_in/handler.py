import logging
from typing import Final

from account.application.log_in.command import LogInCommand, LogInResult
from account.application.log_in.port import LogInUseCase
from account.application.shared.token_pair_issuer import TokenPairIssuer
from account.domain.account.entity import Account
from account.domain.account.errors import AccountNotFoundByEmailError
from account.domain.account.repository import AccountRepository
from account.domain.account.value_objects import Email, RawPassword

log = logging.getLogger(__name__)

AUTH_ACCOUNT_INACTIVE: Final[str] = "Your account is inactive. Please contact support."


class AuthenticationError(Exception):
    pass


class LogInHandler(LogInUseCase):
    def __init__(
        self,
        account_repository: AccountRepository,
        token_pair_issuer: TokenPairIssuer,
    ) -> None:
        self._account_repository = account_repository
        self._token_pair_issuer = token_pair_issuer

    async def execute(self, command: LogInCommand) -> LogInResult:
        log.info("Log in: started. Email: '%s'.", command.email)

        email = Email(command.email)
        password = RawPassword(command.password)

        account: Account | None = await self._account_repository.get_by_email(email)
        if account is None:
            raise AccountNotFoundByEmailError(email)

        if not account.is_active:
            raise AuthenticationError(AUTH_ACCOUNT_INACTIVE)

        access_token, refresh_token = await self._token_pair_issuer.issue_token_pair(
            email, password
        )

        log.info(
            "Log in: done. Account, ID: '%s', email '%s', role '%s'.",
            account.id_.value,
            account.email.value,
            account.role.value,
        )

        return LogInResult(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._token_pair_issuer.access_token_expiry_seconds,
        )
