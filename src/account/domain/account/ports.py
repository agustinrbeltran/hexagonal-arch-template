from abc import abstractmethod
from typing import Protocol

from shared.domain.account_id import AccountId

from account.domain.account.value_objects import AccountPasswordHash, RawPassword


class PasswordHasher(Protocol):
    @abstractmethod
    async def hash(self, raw_password: RawPassword) -> AccountPasswordHash:
        """:raises PasswordHasherBusyError:"""

    @abstractmethod
    async def verify(
        self,
        raw_password: RawPassword,
        hashed_password: AccountPasswordHash,
    ) -> bool:
        """:raises PasswordHasherBusyError:"""


class AccessRevoker(Protocol):
    @abstractmethod
    async def remove_all_account_access(self, account_id: AccountId) -> None:
        """:raises DataMapperError:"""


class AccountIdGenerator:
    @abstractmethod
    def generate(self) -> AccountId: ...
