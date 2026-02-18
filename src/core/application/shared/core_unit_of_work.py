from abc import abstractmethod
from typing import Protocol


class CoreUnitOfWork(Protocol):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
