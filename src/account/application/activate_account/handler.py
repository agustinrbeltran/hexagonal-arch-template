import logging

from account.application.activate_account.command import ActivateAccountCommand
from account.application.activate_account.port import ActivateAccountUseCase
from account.application.current_account.handler import CurrentAccountHandler
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.errors import AccountNotFoundByIdError
from account.domain.account.repository import AccountRepository
from account.domain.account.services import (
    AccountManagementContext,
    CanManageRole,
    CanManageSubordinate,
    RoleManagementContext,
    authorize,
)
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.account_id import AccountId

log = logging.getLogger(__name__)


class ActivateAccountHandler(ActivateAccountUseCase):
    def __init__(
        self,
        current_account_handler: CurrentAccountHandler,
        account_repository: AccountRepository,
        account_unit_of_work: AccountUnitOfWork,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self._current_account_handler = current_account_handler
        self._account_repository = account_repository
        self._account_unit_of_work = account_unit_of_work
        self._event_dispatcher = event_dispatcher

    async def execute(self, command: ActivateAccountCommand) -> None:
        log.info(
            "Activate account: started. Target account ID: '%s'.",
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

        if account.activate():
            await self._account_unit_of_work.commit()

        await self._event_dispatcher.dispatch(account.collect_events())

        log.info("Activate account: done. Target account ID: '%s'.", account.id_.value)
