import logging
from typing import Final

from account.application.change_password.command import ChangePasswordCommand
from account.application.change_password.port import ChangePasswordUseCase
from account.application.current_account.handler import CurrentAccountHandler
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.domain.account.repository import AccountRepository
from account.domain.account.services import AccountService
from account.domain.account.value_objects import RawPassword
from shared.application.event_dispatcher import EventDispatcher

log = logging.getLogger(__name__)

AUTH_INVALID_CURRENT_CREDENTIAL: Final[str] = "Invalid password."
AUTH_NEW_CREDENTIAL_SAME_AS_CURRENT: Final[str] = (
    "New password must differ from current password."
)


class AuthenticationChangeError(Exception):
    pass


class ReAuthenticationError(Exception):
    pass


class ChangePasswordHandler(ChangePasswordUseCase):
    def __init__(
        self,
        current_account_handler: CurrentAccountHandler,
        account_service: AccountService,
        account_repository: AccountRepository,
        account_unit_of_work: AccountUnitOfWork,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self._current_account_handler = current_account_handler
        self._account_service = account_service
        self._account_repository = account_repository
        self._account_unit_of_work = account_unit_of_work
        self._event_dispatcher = event_dispatcher

    async def execute(self, command: ChangePasswordCommand) -> None:
        log.info("Change password: started.")

        current_account = await self._current_account_handler.get_current_account(
            for_update=True,
        )

        current_password = RawPassword(command.current_password)
        new_password = RawPassword(command.new_password)
        if current_password == new_password:
            raise AuthenticationChangeError(AUTH_NEW_CREDENTIAL_SAME_AS_CURRENT)

        if not await self._account_service.is_password_valid(
            current_account,
            current_password,
        ):
            raise ReAuthenticationError(AUTH_INVALID_CURRENT_CREDENTIAL)

        await self._account_service.change_password(current_account, new_password)
        self._account_repository.save(current_account)
        await self._event_dispatcher.dispatch(current_account.collect_events())
        await self._account_unit_of_work.commit()

        log.info("Change password: done. Account ID: '%s'.", current_account.id_.value)
