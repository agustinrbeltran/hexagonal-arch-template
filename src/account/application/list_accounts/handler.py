import logging

from account.application.current_account.handler import CurrentAccountHandler
from account.application.list_accounts.port import ListAccountsUseCase
from account.application.list_accounts.query import ListAccountsQuery
from account.domain.account.enums import AccountRole
from account.domain.account.repository import AccountRepository, ListAccountsQM
from account.domain.account.services import (
    CanManageRole,
    RoleManagementContext,
    authorize,
)
from shared.domain.queries import OffsetPaginationParams, SortingParams

log = logging.getLogger(__name__)


class ListAccountsHandler(ListAccountsUseCase):
    def __init__(
        self,
        current_account_handler: CurrentAccountHandler,
        account_repository: AccountRepository,
    ) -> None:
        self._current_account_handler = current_account_handler
        self._account_repository = account_repository

    async def execute(self, query: ListAccountsQuery) -> ListAccountsQM:
        log.info("List accounts: started.")

        current_account = await self._current_account_handler.get_current_account()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_account,
                target_role=AccountRole.USER,
            ),
        )

        log.debug("Retrieving list of accounts.")
        pagination = OffsetPaginationParams(
            limit=query.limit,
            offset=query.offset,
        )
        sorting = SortingParams(
            field=query.sorting_field,
            order=query.sorting_order,
        )
        response = await self._account_repository.get_all(
            pagination=pagination,
            sorting=sorting,
        )

        log.info("List accounts: done.")
        return response
