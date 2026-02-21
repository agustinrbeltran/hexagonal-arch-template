import logging

from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.application.update_profile.command import UpdateProfileCommand
from core.application.update_profile.port import UpdateProfileUseCase
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from core.domain.profile.repository import ProfileRepository
from core.domain.profile.value_objects import BirthDate, FirstName, LastName, Username
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.ports.identity_provider import IdentityProvider

log = logging.getLogger(__name__)


class UpdateProfileHandler(UpdateProfileUseCase):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        profile_repository: ProfileRepository,
        core_unit_of_work: CoreUnitOfWork,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self._identity_provider = identity_provider
        self._profile_repository = profile_repository
        self._core_unit_of_work = core_unit_of_work
        self._event_dispatcher = event_dispatcher

    async def execute(self, command: UpdateProfileCommand) -> None:
        log.info("Update profile: started.")

        account_id = await self._identity_provider.get_current_account_id()
        profile = await self._profile_repository.get_by_account_id(
            account_id, for_update=True
        )
        if profile is None:
            raise ProfileNotFoundByAccountIdError(account_id)

        first_name = (
            FirstName(command.first_name) if command.first_name is not None else None
        )
        last_name = (
            LastName(command.last_name) if command.last_name is not None else None
        )
        birth_date = (
            BirthDate(command.birth_date) if command.birth_date is not None else None
        )
        username = Username(command.username) if command.username is not None else None

        profile.update(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            username=username,
        )
        await self._profile_repository.save(profile)

        await self._event_dispatcher.dispatch(profile.collect_events())
        await self._core_unit_of_work.commit()

        log.info("Update profile: done. Profile ID: '%s'.", profile.id_.value)
