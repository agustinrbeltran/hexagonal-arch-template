import logging

from core.application.patch_profile.command import PatchProfileCommand
from core.application.patch_profile.port import PatchProfileUseCase
from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from core.domain.profile.repository import ProfileRepository
from core.domain.profile.value_objects import BirthDate, FirstName, LastName, Username
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.ports.identity_provider import IdentityProvider
from shared.domain.unset import UNSET, _Unset

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

        first_name: FirstName | None | _Unset
        if isinstance(command.first_name, _Unset):
            first_name = UNSET
        elif command.first_name is None:
            first_name = None
        else:
            first_name = FirstName(command.first_name)

        last_name: LastName | None | _Unset
        if isinstance(command.last_name, _Unset):
            last_name = UNSET
        elif command.last_name is None:
            last_name = None
        else:
            last_name = LastName(command.last_name)

        birth_date: BirthDate | None | _Unset
        if isinstance(command.birth_date, _Unset):
            birth_date = UNSET
        elif command.birth_date is None:
            birth_date = None
        else:
            birth_date = BirthDate(command.birth_date)

        username: Username | None | _Unset
        if isinstance(command.username, _Unset):
            username = UNSET
        elif command.username is None:
            username = None
        else:
            username = Username(command.username)

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
