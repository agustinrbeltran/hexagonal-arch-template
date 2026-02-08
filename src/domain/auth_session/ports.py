from abc import abstractmethod
from typing import Protocol

from domain.auth_session.entity import AuthSession


class AuthSessionTransport(Protocol):
    @abstractmethod
    def deliver(self, auth_session: AuthSession) -> None: ...

    @abstractmethod
    def extract_id(self) -> str | None: ...

    @abstractmethod
    def remove_current(self) -> None: ...


class AuthSessionTransactionManager(Protocol):
    """
    UoW-compatible interface for committing a business transaction.
    May be extended with rollback support.
    """

    @abstractmethod
    async def commit(self) -> None:
        """:raises DataMapperError:"""
