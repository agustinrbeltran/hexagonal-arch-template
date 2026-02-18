from abc import ABC, abstractmethod

from account.application.log_in.command import LogInCommand, LogInResult


class LogInUseCase(ABC):
    @abstractmethod
    async def execute(self, command: LogInCommand) -> LogInResult: ...
