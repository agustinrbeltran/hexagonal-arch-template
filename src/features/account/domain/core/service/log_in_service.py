import logging

from features.account.domain.core.services.auth_session_service import (
    AuthSessionService,
)
from features.account.domain.port.inbound.log_in_use_case import (
    LogInCommand,
    LogInUseCase,
)
from features.user.adapter.exceptions.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from features.user.domain.core.constants import (
    AUTH_ACCOUNT_INACTIVE,
    AUTH_ALREADY_AUTHENTICATED,
    AUTH_PASSWORD_INVALID,
)
from features.user.domain.core.entities.user import User
from features.user.domain.core.exceptions.user import UserNotFoundByUsernameError
from features.user.domain.core.service.current_user_service import CurrentUserService
from features.user.domain.core.service.user_service import UserService
from features.user.domain.core.vo.raw_password import RawPassword
from features.user.domain.core.vo.username import Username
from features.user.domain.port.outbound.user_repository import UserRepository

log = logging.getLogger(__name__)


class LogInService(LogInUseCase):
    """
    - Open to everyone.
    - Authenticates registered user,
    sets a JWT access token with a session ID in cookies,
    and creates a session.
    - A logged-in user cannot log in again
    until the session expires or is terminated.
    - Authentication renews automatically
    when accessing protected routes before expiration.
    - If the JWT is invalid, expired, or the session is terminated,
    the user loses authentication.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_repository: UserRepository,
        user_service: UserService,
        auth_session_service: AuthSessionService,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_repository = user_repository
        self._user_service = user_service
        self._auth_session_service = auth_session_service

    async def execute(self, command: LogInCommand) -> None:
        """
        :raises AlreadyAuthenticatedError:
        :raises AuthorizationError:
        :raises DataMapperError:
        :raises DomainTypeError:
        :raises UserNotFoundByUsernameError:
        :raises PasswordHasherBusyError:
        :raises AuthenticationError:
        """
        log.info("Log in: started. Username: '%s'.", command.username)

        try:
            await self._current_user_service.get_current_user()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except AuthenticationError:
            pass

        username = Username(command.username)
        password = RawPassword(command.password)

        user: User | None = await self._user_repository.get_by_username(username)
        if user is None:
            raise UserNotFoundByUsernameError(username)

        if not await self._user_service.is_password_valid(user, password):
            raise AuthenticationError(AUTH_PASSWORD_INVALID)

        if not user.is_active:
            raise AuthenticationError(AUTH_ACCOUNT_INACTIVE)

        await self._auth_session_service.issue_session(user.id_)

        log.info(
            "Log in: done. User, ID: '%s', username '%s', role '%s'.",
            user.id_.value,
            user.username.value,
            user.role.value,
        )
