from dataclasses import dataclass
from enum import StrEnum

from domain.shared.errors import DomainError


class PaginationError(DomainError):
    pass


class SortingError(DomainError):
    pass


class SortingOrder(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True, slots=True, kw_only=True)
class OffsetPaginationParams:
    """
    raises PaginationError
    """

    limit: int
    offset: int

    def __post_init__(self):
        """:raises PaginationError:"""
        if self.limit <= 0:
            raise PaginationError(f"Limit must be greater than 0, got {self.limit}")
        if self.offset < 0:
            raise PaginationError(f"Offset must be non-negative, got {self.offset}")


@dataclass(frozen=True, slots=True, kw_only=True)
class SortingParams:
    field: str
    order: SortingOrder
