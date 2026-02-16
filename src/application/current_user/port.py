from abc import ABC, abstractmethod

from domain.user.entity import User


class CurrentUserUseCase(ABC):
    @abstractmethod
    async def get_current_user(self, for_update: bool = False) -> User: ...
