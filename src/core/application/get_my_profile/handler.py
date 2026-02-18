import logging

from core.application.get_my_profile.port import GetMyProfileResponse, GetMyProfileUseCase
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from core.domain.profile.repository import ProfileRepository
from shared.domain.ports.identity_provider import IdentityProvider

log = logging.getLogger(__name__)


class GetMyProfileHandler(GetMyProfileUseCase):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        profile_repository: ProfileRepository,
    ) -> None:
        self._identity_provider = identity_provider
        self._profile_repository = profile_repository

    async def execute(self) -> GetMyProfileResponse:
        log.info("Get my profile: started.")

        account_id = await self._identity_provider.get_current_account_id()
        profile = await self._profile_repository.get_by_account_id(account_id)
        if profile is None:
            raise ProfileNotFoundByAccountIdError(account_id)

        log.info("Get my profile: done. Profile ID: '%s'.", profile.id_.value)
        return GetMyProfileResponse(
            id=profile.id_.value,
            account_id=profile.account_id.value,
            username=profile.username.value if profile.username else None,
        )
