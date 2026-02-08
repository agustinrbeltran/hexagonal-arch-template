import logging

from application.current_user.handler import CurrentUserHandler
from application.list_users.port import ListUsersUseCase
from application.list_users.query import ListUsersQuery
from domain.shared.queries import OffsetPaginationParams, SortingParams
from domain.user.enums import UserRole
from domain.user.repository import ListUsersQM, UserRepository
from domain.user.services import (
    CanManageRole,
    RoleManagementContext,
    authorize,
)

log = logging.getLogger(__name__)


class ListUsersHandler(ListUsersUseCase):
    def __init__(
        self,
        current_user_handler: CurrentUserHandler,
        user_repository: UserRepository,
    ) -> None:
        self._current_user_handler = current_user_handler
        self._user_repository = user_repository

    async def execute(self, query: ListUsersQuery) -> ListUsersQM:
        log.info("List users: started.")

        current_user = await self._current_user_handler.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )

        log.debug("Retrieving list of users.")
        pagination = OffsetPaginationParams(
            limit=query.limit,
            offset=query.offset,
        )
        sorting = SortingParams(
            field=query.sorting_field,
            order=query.sorting_order,
        )
        response = await self._user_repository.get_all(
            pagination=pagination,
            sorting=sorting,
        )

        log.info("List users: done.")
        return response
