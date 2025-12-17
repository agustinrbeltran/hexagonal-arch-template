from abc import abstractmethod
from typing import Protocol

from features.account.domain.core.entities.auth_session import AuthSession
from features.user.domain.core.vo.user_id import UserId


class AuthSessionGateway(Protocol):
    """
    Defined to allow easier mocking and swapping
    of implementations in the same layer.
    """

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
