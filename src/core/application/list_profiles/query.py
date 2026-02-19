from dataclasses import dataclass

from shared.domain.queries import SortingOrder


@dataclass(frozen=True, slots=True, kw_only=True)
class ListProfilesQuery:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder
