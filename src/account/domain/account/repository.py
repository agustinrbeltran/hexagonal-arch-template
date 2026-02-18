from abc import abstractmethod
from typing import Protocol, TypedDict
from uuid import UUID

from account.domain.account.enums import AccountRole
from account.domain.account.value_objects import Email
from shared.domain.account_id import AccountId
from shared.domain.queries import OffsetPaginationParams, SortingParams


class AccountQueryModel(TypedDict):
    id_: UUID
    email: str
    role: AccountRole
    is_active: bool


class ListAccountsQM(TypedDict):
    accounts: list[AccountQueryModel]
    total: int


class AccountRepository(Protocol):
    @abstractmethod
    def save(self, account: "Account") -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_by_id(
        self,
        account_id: AccountId,
        for_update: bool = False,
    ) -> "Account | None":
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_by_email(
        self,
        email: Email,
        for_update: bool = False,
    ) -> "Account | None":
        """:raises DataMapperError:"""

    @abstractmethod
    async def get_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListAccountsQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """


from account.domain.account.entity import Account  # noqa: E402
