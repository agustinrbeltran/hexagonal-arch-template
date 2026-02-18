from abc import abstractmethod
from typing import Protocol

from account.infrastructure.security.refresh_token import RefreshToken
from shared.domain.account_id import AccountId


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
    async def delete_all_for_account(self, account_id: AccountId) -> None:
        """:raises DataMapperError:"""
