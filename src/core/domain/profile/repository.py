from abc import abstractmethod
from typing import Protocol, TypedDict
from uuid import UUID

from shared.domain.account_id import AccountId
from shared.domain.queries import OffsetPaginationParams, SortingParams

from core.domain.profile.value_objects import ProfileId


class ProfileQueryModel(TypedDict):
    id_: UUID
    account_id: UUID
    username: str | None


class ListProfilesQM(TypedDict):
    profiles: list[ProfileQueryModel]
    total: int


class ProfileRepository(Protocol):
    @abstractmethod
    def save(self, profile: "Profile") -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_by_id(
        self,
        profile_id: ProfileId,
        for_update: bool = False,
    ) -> "Profile | None":
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_by_account_id(
        self,
        account_id: AccountId,
        for_update: bool = False,
    ) -> "Profile | None":
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListProfilesQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """


from core.domain.profile.entity import Profile  # noqa: E402, F401
