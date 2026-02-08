from abc import abstractmethod
from typing import Protocol

from domain.auth_session.entity import AuthSession
from domain.user.value_objects import UserId


class AuthSessionGateway(Protocol):
    @abstractmethod
    def add(self, auth_session: AuthSession) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, auth_session_id: str) -> AuthSession | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def update(self, auth_session: AuthSession) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def delete(self, auth_session_id: str) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def delete_all_for_user(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""
