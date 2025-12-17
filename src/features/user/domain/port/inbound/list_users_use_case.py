import logging
from dataclasses import dataclass

from common.domain.port.inbound.queries.offset_pagination import OffsetPaginationParams
from common.domain.port.inbound.queries.sorting import SortingOrder, SortingParams
from features.user.domain.core.enums.user_role import UserRole
from features.user.domain.core.service.current_user_service import CurrentUserService
from features.user.domain.core.service.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from features.user.domain.core.utils.authorize import authorize
from features.user.domain.port.outbound.queries.user_queries import ListUsersQM
from features.user.domain.port.outbound.user_repository import UserRepository

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListUsersQuery:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder


class ListUsersUseCase:
    """
    - Open to admins.
    - Retrieves a paginated list of existing users with relevant information.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_repository: UserRepository,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_repository = user_repository

    async def execute(self, request_data: ListUsersQuery) -> ListUsersQM:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises PaginationError:
        :raises SortingError:
        :raises ReaderError:
        """
        log.info("List users: started.")

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )

        log.debug("Retrieving list of users.")
        pagination = OffsetPaginationParams(
            limit=request_data.limit,
            offset=request_data.offset,
        )
        sorting = SortingParams(
            field=request_data.sorting_field,
            order=request_data.sorting_order,
        )
        response = await self._user_repository.get_all(
            pagination=pagination,
            sorting=sorting,
        )

        log.info("List users: done.")
        return response
