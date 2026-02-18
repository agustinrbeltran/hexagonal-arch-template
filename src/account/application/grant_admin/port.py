from abc import ABC, abstractmethod

from account.application.grant_admin.command import GrantAdminCommand


class GrantAdminUseCase(ABC):
    @abstractmethod
    async def execute(self, command: GrantAdminCommand) -> None: ...
