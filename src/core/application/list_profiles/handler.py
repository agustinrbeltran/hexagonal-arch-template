import logging

from core.application.list_profiles.port import ListProfilesUseCase
from core.application.list_profiles.query import ListProfilesQuery
from core.domain.profile.repository import ListProfilesQM, ProfileRepository
from shared.domain.ports.authorization_guard import AuthorizationGuard
from shared.domain.queries import OffsetPaginationParams, SortingParams

log = logging.getLogger(__name__)


class ListProfilesHandler(ListProfilesUseCase):
    def __init__(
        self,
        authorization_guard: AuthorizationGuard,
        profile_repository: ProfileRepository,
    ) -> None:
        self._authorization_guard = authorization_guard
        self._profile_repository = profile_repository

    async def execute(self, query: ListProfilesQuery) -> ListProfilesQM:
        log.info("List profiles: started.")

        await self._authorization_guard.require_admin()

        pagination = OffsetPaginationParams(
            limit=query.limit,
            offset=query.offset,
        )
        sorting = SortingParams(
            field=query.sorting_field,
            order=query.sorting_order,
        )
        result = await self._profile_repository.get_all(pagination, sorting)

        log.info("List profiles: done. Total: %d.", result["total"])
        return result
