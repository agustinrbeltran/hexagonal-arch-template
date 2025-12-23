from abc import ABC, abstractmethod
from dataclasses import dataclass

from common.domain.port.inbound.queries.sorting import SortingOrder
from features.user.domain.port.outbound.queries.user_queries import ListUsersQM


@dataclass(frozen=True, slots=True, kw_only=True)
class ListUsersQuery:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder


class ListUsersUseCase(ABC):
    """
    - Open to admins.
    - Retrieves a paginated list of existing users with relevant information.
    """

    @abstractmethod
    async def execute(self, query: ListUsersQuery) -> ListUsersQM:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises PaginationError:
        :raises SortingError:
        :raises ReaderError:
        """
        pass
