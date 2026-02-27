from abc import abstractmethod
from typing import Protocol

from shared.domain.account_id import AccountId


class AccessRevoker(Protocol):
    @abstractmethod
    async def remove_all_account_access(self, account_id: AccountId) -> None:
        """:raises DataMapperError:"""
