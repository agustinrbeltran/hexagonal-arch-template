from abc import ABC, abstractmethod

from application.list_users.query import ListUsersQuery
from domain.user.repository import ListUsersQM


class ListUsersUseCase(ABC):
    @abstractmethod
    async def execute(self, query: ListUsersQuery) -> ListUsersQM: ...
