from dataclasses import dataclass

from domain.shared.queries import SortingOrder


@dataclass(frozen=True, slots=True, kw_only=True)
class ListUsersQuery:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder
