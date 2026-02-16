from abc import ABC, abstractmethod

from application.activate_user.command import ActivateUserCommand


class ActivateUserUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ActivateUserCommand) -> None: ...
