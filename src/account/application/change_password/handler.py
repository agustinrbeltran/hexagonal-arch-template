import logging

from account.application.change_password.command import ChangePasswordCommand
from account.application.change_password.port import ChangePasswordUseCase
from account.application.current_account.handler import CurrentAccountHandler
from account.application.shared.password_resetter import PasswordResetter
from account.domain.account.value_objects import RawPassword

log = logging.getLogger(__name__)


class ChangePasswordHandler(ChangePasswordUseCase):
    def __init__(
        self,
        current_account_handler: CurrentAccountHandler,
        password_resetter: PasswordResetter,
    ) -> None:
        self._current_account_handler = current_account_handler
        self._password_resetter = password_resetter

    async def execute(self, command: ChangePasswordCommand) -> None:
        log.info("Change password: started.")

        current_account = await self._current_account_handler.get_current_account()

        new_password = RawPassword(command.new_password)

        await self._password_resetter.reset_password(current_account.id_, new_password)

        log.info(
            "Change password: done. Account ID: '%s'.",
            current_account.id_.value,
        )
