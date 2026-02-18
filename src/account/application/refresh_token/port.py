from abc import ABC, abstractmethod

from account.application.refresh_token.command import (
    RefreshTokenCommand,
    RefreshTokenResult,
)


class RefreshTokenUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RefreshTokenCommand) -> RefreshTokenResult: ...
