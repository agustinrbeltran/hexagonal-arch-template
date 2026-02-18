import logging

from account.domain.account.events import AccountCreated
from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.domain.profile.entity import Profile
from core.domain.profile.ports import ProfileIdGenerator
from core.domain.profile.repository import ProfileRepository
from shared.domain.account_id import AccountId
from shared.infrastructure.events.registry import handles

log = logging.getLogger(__name__)


@handles(AccountCreated)
class CreateProfileOnAccountCreated:
    def __init__(
        self,
        profile_id_generator: ProfileIdGenerator,
        profile_repository: ProfileRepository,
        core_unit_of_work: CoreUnitOfWork,
    ) -> None:
        self._profile_id_generator = profile_id_generator
        self._profile_repository = profile_repository
        self._core_unit_of_work = core_unit_of_work

    async def handle(self, event: AccountCreated) -> None:
        log.info(
            "Creating profile for new account: account_id=%s.", event.account_id
        )

        profile_id = self._profile_id_generator.generate()
        account_id = AccountId(event.account_id)

        profile = Profile.create(id_=profile_id, account_id=account_id)
        self._profile_repository.save(profile)
        await self._core_unit_of_work.commit()

        log.info(
            "Profile created: profile_id=%s, account_id=%s.",
            profile_id.value,
            event.account_id,
        )
