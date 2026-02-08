from abc import ABC, abstractmethod


class LogOutUseCase(ABC):
    @abstractmethod
    async def execute(self) -> None: ...
