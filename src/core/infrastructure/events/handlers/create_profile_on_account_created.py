from account.domain.account.events import AccountCreated
from core.application.create_profile.command import CreateProfileCommand
from core.application.create_profile.port import CreateProfileUseCase
from shared.infrastructure.events.registry import handles


@handles(AccountCreated)
class CreateProfileOnAccountCreated:
    def __init__(self, create_profile: CreateProfileUseCase) -> None:
        self._create_profile = create_profile

    async def handle(self, event: AccountCreated) -> None:
        command = CreateProfileCommand(account_id=event.account_id)
        await self._create_profile.execute(command)
