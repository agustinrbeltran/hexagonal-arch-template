from abc import abstractmethod
from typing import Protocol

from shared.domain.account_id import AccountId


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_account_id(self) -> AccountId:
        """:raises AuthenticationError:"""
