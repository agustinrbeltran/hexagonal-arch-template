from abc import ABC, abstractmethod
from typing import TypedDict
from uuid import UUID


class GetMyProfileResponse(TypedDict):
    id: UUID
    account_id: UUID
    username: str | None


class GetMyProfileUseCase(ABC):
    @abstractmethod
    async def execute(self) -> GetMyProfileResponse: ...
