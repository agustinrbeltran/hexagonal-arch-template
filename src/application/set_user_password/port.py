from abc import ABC, abstractmethod

from application.set_user_password.command import SetUserPasswordCommand


class SetUserPasswordUseCase(ABC):
    @abstractmethod
    async def execute(self, command: SetUserPasswordCommand) -> None: ...
