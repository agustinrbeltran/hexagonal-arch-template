import logging
from typing import Final

from application.current_user.handler import CurrentUserHandler
from application.log_in.command import LogInCommand
from application.log_in.port import LogInUseCase
from application.sign_up.handler import AlreadyAuthenticatedError
from domain.auth_session.services import AuthSessionService
from domain.shared.errors import AuthorizationError
from domain.user.entity import User
from domain.user.errors import UserNotFoundByUsernameError
from domain.user.repository import UserRepository
from domain.user.services import UserService
from domain.user.value_objects import RawPassword, Username

log = logging.getLogger(__name__)

AUTH_ALREADY_AUTHENTICATED: Final[str] = (
    "You are already authenticated. Consider logging out."
)
AUTH_INVALID_CREDENTIAL: Final[str] = "Invalid password."
AUTH_ACCOUNT_INACTIVE: Final[str] = "Your account is inactive. Please contact support."


class AuthenticationError(Exception):
    pass


class LogInHandler(LogInUseCase):
    def __init__(
        self,
        current_user_handler: CurrentUserHandler,
        user_repository: UserRepository,
        user_service: UserService,
        auth_session_service: AuthSessionService,
    ) -> None:
        self._current_user_handler = current_user_handler
        self._user_repository = user_repository
        self._user_service = user_service
        self._auth_session_service = auth_session_service

    async def execute(self, command: LogInCommand) -> None:
        log.info("Log in: started. Username: '%s'.", command.username)

        try:
            await self._current_user_handler.get_current_user()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except (AuthorizationError, Exception) as err:
            if isinstance(err, AlreadyAuthenticatedError):
                raise
            pass

        username = Username(command.username)
        password = RawPassword(command.password)

        user: User | None = await self._user_repository.get_by_username(username)
        if user is None:
            raise UserNotFoundByUsernameError(username)

        if not await self._user_service.is_password_valid(user, password):
            raise AuthenticationError(AUTH_INVALID_CREDENTIAL)

        if not user.is_active:
            raise AuthenticationError(AUTH_ACCOUNT_INACTIVE)

        await self._auth_session_service.issue_session(user.id_)

        log.info(
            "Log in: done. User, ID: '%s', username '%s', role '%s'.",
            user.id_.value,
            user.username.value,
            user.role.value,
        )
