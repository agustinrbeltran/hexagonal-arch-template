from abc import ABC, abstractmethod

from application.deactivate_user.command import DeactivateUserCommand


class DeactivateUserUseCase(ABC):
    @abstractmethod
    async def execute(self, command: DeactivateUserCommand) -> None: ...
