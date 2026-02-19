from abc import ABC, abstractmethod

from core.application.set_username.command import SetUsernameCommand


class SetUsernameUseCase(ABC):
    @abstractmethod
    async def execute(self, command: SetUsernameCommand) -> None: ...
