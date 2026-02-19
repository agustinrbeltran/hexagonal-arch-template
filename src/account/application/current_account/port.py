from abc import ABC, abstractmethod

from account.domain.account.entity import Account


class CurrentAccountUseCase(ABC):
    @abstractmethod
    async def get_current_account(self, for_update: bool = False) -> Account: ...
