from abc import ABC, abstractmethod

from account.application.create_account.command import (
    CreateAccountCommand,
    CreateAccountResponse,
)


class CreateAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateAccountCommand) -> CreateAccountResponse: ...
