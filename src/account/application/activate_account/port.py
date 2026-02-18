from abc import ABC, abstractmethod

from account.application.activate_account.command import ActivateAccountCommand


class ActivateAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ActivateAccountCommand) -> None: ...
