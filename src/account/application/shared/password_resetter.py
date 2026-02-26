from abc import abstractmethod
from typing import Protocol

from account.domain.account.value_objects import RawPassword
from shared.domain.account_id import AccountId


class PasswordResetter(Protocol):
    @abstractmethod
    async def reset_password(
        self, account_id: AccountId, new_password: RawPassword
    ) -> None: ...
