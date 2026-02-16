import logging
from typing import Final

from application.log_in.command import LogInCommand, LogInResult
from application.log_in.port import LogInUseCase
from domain.refresh_token.services import RefreshTokenService
from domain.user.entity import User
from domain.user.errors import UserNotFoundByUsernameError
from domain.user.repository import UserRepository
from domain.user.services import UserService
from domain.user.value_objects import RawPassword, Username

log = logging.getLogger(__name__)

AUTH_INVALID_CREDENTIAL: Final[str] = "Invalid password."
AUTH_ACCOUNT_INACTIVE: Final[str] = "Your account is inactive. Please contact support."


class AuthenticationError(Exception):
    pass


class LogInHandler(LogInUseCase):
    def __init__(
        self,
        user_repository: UserRepository,
        user_service: UserService,
        refresh_token_service: RefreshTokenService,
    ) -> None:
        self._user_repository = user_repository
        self._user_service = user_service
        self._refresh_token_service = refresh_token_service

    async def execute(self, command: LogInCommand) -> LogInResult:
        log.info("Log in: started. Username: '%s'.", command.username)

        username = Username(command.username)
        password = RawPassword(command.password)

        user: User | None = await self._user_repository.get_by_username(username)
        if user is None:
            raise UserNotFoundByUsernameError(username)

        if not await self._user_service.is_password_valid(user, password):
            raise AuthenticationError(AUTH_INVALID_CREDENTIAL)

        if not user.is_active:
            raise AuthenticationError(AUTH_ACCOUNT_INACTIVE)

        access_token, refresh_token = self._refresh_token_service.issue_token_pair(
            user.id_
        )

        log.info(
            "Log in: done. User, ID: '%s', username '%s', role '%s'.",
            user.id_.value,
            user.username.value,
            user.role.value,
        )

        return LogInResult(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._refresh_token_service._access_token_expiry_min * 60,
        )
