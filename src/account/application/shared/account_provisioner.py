from abc import abstractmethod
from typing import Protocol

from account.domain.account.value_objects import Email, RawPassword
from shared.domain.account_id import AccountId


class AccountProvisioner(Protocol):
    @abstractmethod
    async def register(self, email: Email, password: RawPassword) -> AccountId:
        """:raises EmailAlreadyExistsError:"""
