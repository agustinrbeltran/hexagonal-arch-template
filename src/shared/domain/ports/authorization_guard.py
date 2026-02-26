from abc import abstractmethod
from typing import Protocol


class AuthorizationGuard(Protocol):
    @abstractmethod
    async def require_admin(self) -> None:
        """:raises AuthorizationError:"""
