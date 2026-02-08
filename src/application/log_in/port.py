from abc import ABC, abstractmethod

from application.log_in.command import LogInCommand


class LogInUseCase(ABC):
    @abstractmethod
    async def execute(self, command: LogInCommand) -> None: ...
