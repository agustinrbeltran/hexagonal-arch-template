import logging

from account.domain.account.enums import AccountRole
from account.domain.account.repository import AccountRepository
from core.application.list_profiles.port import ListProfilesUseCase
from core.application.list_profiles.query import ListProfilesQuery
from core.domain.profile.repository import ListProfilesQM, ProfileRepository
from shared.domain.errors import AuthorizationError
from shared.domain.ports.identity_provider import IdentityProvider
from shared.domain.queries import OffsetPaginationParams, SortingParams

log = logging.getLogger(__name__)


class ListProfilesHandler(ListProfilesUseCase):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        account_repository: AccountRepository,
        profile_repository: ProfileRepository,
    ) -> None:
        self._identity_provider = identity_provider
        self._account_repository = account_repository
        self._profile_repository = profile_repository

    async def execute(self, query: ListProfilesQuery) -> ListProfilesQM:
        log.info("List profiles: started.")

        account_id = await self._identity_provider.get_current_account_id()
        account = await self._account_repository.get_by_id(account_id)
        if account is None or account.role not in {
            AccountRole.SUPER_ADMIN,
            AccountRole.ADMIN,
        }:
            raise AuthorizationError("Insufficient permissions to list profiles.")

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
