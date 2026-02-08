from abc import abstractmethod
from typing import Protocol, TypedDict
from uuid import UUID

from domain.shared.queries import OffsetPaginationParams, SortingParams
from domain.user.entity import User
from domain.user.enums import UserRole
from domain.user.value_objects import UserId, Username


class UserQueryModel(TypedDict):
    id_: UUID
    username: str
    role: UserRole
    is_active: bool


class ListUsersQM(TypedDict):
    users: list[UserQueryModel]
    total: int


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
