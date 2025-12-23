from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ActivateUserCommand:
    user_id: UUID


class ActivateUserUseCase(ABC):
    """
    - Open to admins.
    - Restores a previously soft-deleted user.
    - Only super admins can activate other admins.
    """

    @abstractmethod
    async def execute(self, command: ActivateUserCommand) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises UserNotFoundByIdError:
        :raises ActivationChangeNotPermittedError:
        """
        pass
