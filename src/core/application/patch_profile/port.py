from abc import ABC, abstractmethod

from core.application.patch_profile.command import PatchProfileCommand


class PatchProfileUseCase(ABC):
    """Apply a partial update to the authenticated user's profile."""

    @abstractmethod
    async def execute(self, command: PatchProfileCommand) -> None: ...
