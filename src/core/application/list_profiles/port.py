from abc import ABC, abstractmethod

from core.application.list_profiles.query import ListProfilesQuery
from core.domain.profile.repository import ListProfilesQM


class ListProfilesUseCase(ABC):
    @abstractmethod
    async def execute(self, query: ListProfilesQuery) -> ListProfilesQM: ...
