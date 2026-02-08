from abc import ABC, abstractmethod

from application.change_password.command import ChangePasswordCommand


class ChangePasswordUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ChangePasswordCommand) -> None: ...
