from abc import ABC, abstractmethod

from account.application.sign_up.command import SignUpCommand, SignUpResponse


class SignUpUseCase(ABC):
    @abstractmethod
    async def execute(self, command: SignUpCommand) -> SignUpResponse: ...
