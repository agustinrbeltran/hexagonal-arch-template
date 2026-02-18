import logging

from account.application.current_account.handler import CurrentAccountHandler
from account.application.set_account_password.command import SetAccountPasswordCommand
from account.application.set_account_password.port import SetAccountPasswordUseCase
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.errors import AccountNotFoundByIdError
from account.domain.account.repository import AccountRepository
from account.domain.account.services import (
    AccountManagementContext,
    AccountService,
    CanManageRole,
    CanManageSubordinate,
    RoleManagementContext,
    authorize,
)
from account.domain.account.value_objects import RawPassword
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.account_id import AccountId

log = logging.getLogger(__name__)


class SetAccountPasswordHandler(SetAccountPasswordUseCase):
    def __init__(
        self,
        current_account_handler: CurrentAccountHandler,
        account_repository: AccountRepository,
        account_service: AccountService,
        account_unit_of_work: AccountUnitOfWork,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self._current_account_handler = current_account_handler
        self._account_repository = account_repository
        self._account_service = account_service
        self._account_unit_of_work = account_unit_of_work
        self._event_dispatcher = event_dispatcher

    async def execute(self, command: SetAccountPasswordCommand) -> None:
        log.info(
            "Set account password: started. Target account ID: '%s'.",
            command.account_id,
        )

        current_account = await self._current_account_handler.get_current_account()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_account,
                target_role=AccountRole.USER,
            ),
        )

        account_id = AccountId(command.account_id)
        password = RawPassword(command.password)
        account: Account | None = await self._account_repository.get_by_id(
            account_id,
            for_update=True,
        )
        if account is None:
            raise AccountNotFoundByIdError(account_id)

        authorize(
            CanManageSubordinate(),
            context=AccountManagementContext(
                subject=current_account,
                target=account,
            ),
        )

        await self._account_service.change_password(account, password)
        await self._account_unit_of_work.commit()

        await self._event_dispatcher.dispatch(account.collect_events())

        log.info(
            "Set account password: done. Target account ID: '%s'.", account.id_.value
        )
