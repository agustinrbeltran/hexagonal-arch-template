from abc import ABC, abstractmethod

from account.application.deactivate_account.command import DeactivateAccountCommand


class DeactivateAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, command: DeactivateAccountCommand) -> None: ...
