from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GrantAdminCommand:
    user_id: UUID


class GrantAdminUseCase(ABC):
    """
    - Open to super admins.
    - Grants admin rights to a specified user.
    - Super admin rights cannot be changed.
    """

    @abstractmethod
    async def execute(self, command: GrantAdminCommand) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises UserNotFoundByIdError:
        :raises RoleChangeNotPermittedError:
        """
        pass
