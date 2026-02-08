import logging
from typing import Final

from application.change_password.command import ChangePasswordCommand
from application.change_password.port import ChangePasswordUseCase
from application.current_user.handler import CurrentUserHandler
from application.shared.unit_of_work import UnitOfWork
from domain.user.services import UserService
from domain.user.value_objects import RawPassword

log = logging.getLogger(__name__)

AUTH_PASSWORD_INVALID: Final[str] = "Invalid password."
AUTH_PASSWORD_NEW_SAME_AS_CURRENT: Final[str] = (
    "New password must differ from current password."
)


class AuthenticationChangeError(Exception):
    pass


class ReAuthenticationError(Exception):
    pass


class ChangePasswordHandler(ChangePasswordUseCase):
    def __init__(
        self,
        current_user_handler: CurrentUserHandler,
        user_service: UserService,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._current_user_handler = current_user_handler
        self._user_service = user_service
        self._unit_of_work = unit_of_work

    async def execute(self, command: ChangePasswordCommand) -> None:
        log.info("Change password: started.")

        current_user = await self._current_user_handler.get_current_user(
            for_update=True,
        )

        current_password = RawPassword(command.current_password)
        new_password = RawPassword(command.new_password)
        if current_password == new_password:
            raise AuthenticationChangeError(AUTH_PASSWORD_NEW_SAME_AS_CURRENT)

        if not await self._user_service.is_password_valid(
            current_user,
            current_password,
        ):
            raise ReAuthenticationError(AUTH_PASSWORD_INVALID)

        await self._user_service.change_password(current_user, new_password)
        await self._unit_of_work.commit()

        log.info("Change password: done. User ID: '%s'.", current_user.id_.value)
