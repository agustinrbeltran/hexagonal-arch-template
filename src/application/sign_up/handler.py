import logging
from typing import Final

from application.current_user.handler import CurrentUserHandler
from application.shared.unit_of_work import UnitOfWork
from application.sign_up.command import SignUpCommand, SignUpResponse
from application.sign_up.port import SignUpUseCase
from domain.shared.errors import AuthorizationError
from domain.user.errors import UsernameAlreadyExistsError
from domain.user.repository import UserRepository
from domain.user.services import UserService
from domain.user.value_objects import RawPassword, Username

log = logging.getLogger(__name__)

AUTH_ALREADY_AUTHENTICATED: Final[str] = (
    "You are already authenticated. Consider logging out."
)


class AlreadyAuthenticatedError(Exception):
    pass


class SignUpHandler(SignUpUseCase):
    def __init__(
        self,
        current_user_handler: CurrentUserHandler,
        user_service: UserService,
        user_repository: UserRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._current_user_handler = current_user_handler
        self._user_service = user_service
        self._user_repository = user_repository
        self._unit_of_work = unit_of_work

    async def execute(self, command: SignUpCommand) -> SignUpResponse:
        log.info("Sign up: started. Username: '%s'.", command.username)

        try:
            await self._current_user_handler.get_current_user()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except (AuthorizationError, Exception) as err:
            if isinstance(err, AlreadyAuthenticatedError):
                raise
            # Not authenticated — proceed with sign-up
            pass

        username = Username(command.username)
        password = RawPassword(command.password)

        user = await self._user_service.create(username, password)

        self._user_repository.save(user)

        try:
            await self._unit_of_work.commit()
        except UsernameAlreadyExistsError:
            raise

        log.info("Sign up: done. Username: '%s'.", user.username.value)
        return SignUpResponse(id=user.id_.value)
