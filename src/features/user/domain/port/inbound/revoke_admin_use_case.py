from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RevokeAdminCommand:
    user_id: UUID


class RevokeAdminUseCase(ABC):
    """
    - Open to super admins.
    - Revokes admin rights from a specified user.
    - Super admin rights cannot be changed
    """

    @abstractmethod
    async def execute(self, command: RevokeAdminCommand) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises UserNotFoundByIdError:
        :raises RoleChangeNotPermittedError:
        """
        pass
