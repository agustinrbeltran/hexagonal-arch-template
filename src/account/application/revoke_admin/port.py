from abc import ABC, abstractmethod

from account.application.revoke_admin.command import RevokeAdminCommand


class RevokeAdminUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RevokeAdminCommand) -> None: ...
