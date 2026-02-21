import logging

from core.application.set_username.command import SetUsernameCommand
from core.application.set_username.port import SetUsernameUseCase
from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.domain.profile.errors import ProfileNotFoundByAccountIdError
from core.domain.profile.repository import ProfileRepository
from core.domain.profile.value_objects import Username
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.ports.identity_provider import IdentityProvider

log = logging.getLogger(__name__)


class SetUsernameHandler(SetUsernameUseCase):
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

    async def execute(self, command: SetUsernameCommand) -> None:
        log.info("Set username: started.")

        account_id = await self._identity_provider.get_current_account_id()
        profile = await self._profile_repository.get_by_account_id(
            account_id, for_update=True
        )
        if profile is None:
            raise ProfileNotFoundByAccountIdError(account_id)

        username = Username(command.username)
        profile.set_username(username)
        await self._profile_repository.save(profile)

        await self._event_dispatcher.dispatch(profile.collect_events())
        await self._core_unit_of_work.commit()

        log.info(
            "Set username: done. Profile ID: '%s', username: '%s'.",
            profile.id_.value,
            username.value,
        )
