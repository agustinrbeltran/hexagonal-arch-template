import logging

from core.application.patch_profile.command import PatchProfileCommand
from core.application.patch_profile.port import PatchProfileUseCase
from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from core.domain.profile.repository import ProfileRepository
from core.domain.profile.value_objects import BirthDate, FirstName, LastName, Username
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.ports.identity_provider import IdentityProvider
from shared.domain.unset import UNSET, Unset

log = logging.getLogger(__name__)


class PatchProfileHandler(PatchProfileUseCase):
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

    async def execute(self, command: PatchProfileCommand) -> None:
        log.info("Patch profile: started.")

        account_id = await self._identity_provider.get_current_account_id()
        profile = await self._profile_repository.get_by_account_id(
            account_id, for_update=True
        )
        if profile is None:
            raise ProfileNotFoundByAccountIdError(account_id)

        first_name: FirstName | Unset | None = UNSET
        if not isinstance(command.first_name, Unset):
            first_name = (
                None if command.first_name is None else FirstName(command.first_name)
            )

        last_name: LastName | Unset | None = UNSET
        if not isinstance(command.last_name, Unset):
            last_name = (
                None if command.last_name is None else LastName(command.last_name)
            )

        birth_date: BirthDate | Unset | None = UNSET
        if not isinstance(command.birth_date, Unset):
            birth_date = (
                None if command.birth_date is None else BirthDate(command.birth_date)
            )

        username: Username | Unset | None = UNSET
        if not isinstance(command.username, Unset):
            username = None if command.username is None else Username(command.username)

        profile.apply_patch(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            username=username,
        )
        await self._profile_repository.save(profile)

        await self._event_dispatcher.dispatch(profile.collect_events())
        await self._core_unit_of_work.commit()

        log.info("Patch profile: done. Profile ID: '%s'.", profile.id_.value)
