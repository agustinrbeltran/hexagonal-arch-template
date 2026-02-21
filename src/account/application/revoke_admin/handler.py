import logging

from account.application.current_account.handler import CurrentAccountHandler
from account.application.revoke_admin.command import RevokeAdminCommand
from account.application.revoke_admin.port import RevokeAdminUseCase
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


class RevokeAdminHandler(RevokeAdminUseCase):
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

    async def execute(self, command: RevokeAdminCommand) -> None:
        log.info("Revoke admin: started. Target account ID: '%s'.", command.account_id)

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

        changed = account.change_role(AccountRole.USER)

        if not changed:
            return

        await self._event_dispatcher.dispatch(account.collect_events())
        await self._account_repository.save(account)
        await self._account_unit_of_work.commit()

        log.info("Revoke admin: done. Target account ID: '%s'.", account.id_.value)
