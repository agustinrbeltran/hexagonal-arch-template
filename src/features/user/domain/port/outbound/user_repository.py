from abc import abstractmethod
from typing import Protocol

from common.domain.port.inbound.queries.offset_pagination import OffsetPaginationParams
from common.domain.port.inbound.queries.sorting import SortingParams
from features.user.domain.core.entities.user import User
from features.user.domain.core.vo.user_id import UserId
from features.user.domain.core.vo.username import Username
from features.user.domain.port.outbound.queries.user_queries import ListUsersQM


class UserRepository(Protocol):
    @abstractmethod
    def save(self, user: User) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_by_id(
        self,
        user_id: UserId,
        for_update: bool = False,
    ) -> User | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_by_username(
        self,
        username: Username,
        for_update: bool = False,
    ) -> User | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """
