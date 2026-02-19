from abc import ABC, abstractmethod

from core.application.create_profile.command import CreateProfileCommand


class CreateProfileUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateProfileCommand) -> None: ...
