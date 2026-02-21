from abc import ABC, abstractmethod
from datetime import date
from typing import TypedDict
from uuid import UUID


class GetMyProfileResponse(TypedDict):
    id: UUID
    account_id: UUID
    username: str | None
    first_name: str | None
    last_name: str | None
    birth_date: date | None


class GetMyProfileUseCase(ABC):
    @abstractmethod
    async def execute(self) -> GetMyProfileResponse: ...
