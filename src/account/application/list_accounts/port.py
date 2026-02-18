from abc import ABC, abstractmethod

from account.application.list_accounts.query import ListAccountsQuery
from account.domain.account.repository import ListAccountsQM


class ListAccountsUseCase(ABC):
    @abstractmethod
    async def execute(self, query: ListAccountsQuery) -> ListAccountsQM: ...
