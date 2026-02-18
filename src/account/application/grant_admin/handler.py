import logging

from account.application.current_account.handler import CurrentAccountHandler
from account.application.grant_admin.command import GrantAdminCommand
from account.application.grant_admin.port import GrantAdminUseCase
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.errors import AccountNotFoundByIdError
from account.domain.account.repository import AccountRepository
from account.domain.account.services import (
    CanManageRole,
    RoleManagementContext,
    authorize,
)
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.account_id import AccountId

log = logging.getLogger(__name__)


class GrantAdminHandler(GrantAdminUseCase):
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

    async def execute(self, command: GrantAdminCommand) -> None:
        log.info(
            "Grant admin: started. Target account ID: '%s'.", command.account_id
        )

        current_account = await self._current_account_handler.get_current_account()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_account,
                target_role=AccountRole.ADMIN,
            ),
        )

        account_id = AccountId(command.account_id)
        account: Account | None = await self._account_repository.get_by_id(
            account_id,
            for_update=True,
        )
        if account is None:
            raise AccountNotFoundByIdError(account_id)

        if account.change_role(AccountRole.ADMIN):
            await self._account_unit_of_work.commit()

        await self._event_dispatcher.dispatch(account.collect_events())

        log.info("Grant admin: done. Target account ID: '%s'.", account.id_.value)
