from abc import ABC, abstractmethod

from account.application.set_account_password.command import SetAccountPasswordCommand


class SetAccountPasswordUseCase(ABC):
    @abstractmethod
    async def execute(self, command: SetAccountPasswordCommand) -> None: ...
