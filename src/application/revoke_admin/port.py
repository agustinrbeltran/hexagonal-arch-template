from abc import ABC, abstractmethod

from application.revoke_admin.command import RevokeAdminCommand


class RevokeAdminUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RevokeAdminCommand) -> None: ...
