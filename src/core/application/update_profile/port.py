from abc import ABC, abstractmethod

from core.application.update_profile.command import UpdateProfileCommand


class UpdateProfileUseCase(ABC):
    """Update all mutable fields of the authenticated user's profile."""

    @abstractmethod
    async def execute(self, command: UpdateProfileCommand) -> None: ...
