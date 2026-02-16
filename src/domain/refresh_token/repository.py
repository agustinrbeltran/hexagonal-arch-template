from abc import abstractmethod
from typing import Protocol

from domain.refresh_token.entity import RefreshToken
from domain.user.value_objects import UserId


class RefreshTokenRepository(Protocol):
    @abstractmethod
    def add(self, token: RefreshToken) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_by_id(self, token_id: str) -> RefreshToken | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def delete(self, token_id: str) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def delete_all_for_user(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""
