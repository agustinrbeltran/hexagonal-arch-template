from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class SetUserPasswordCommand:
    user_id: UUID
    password: str


class SetUserPasswordUseCase(ABC):
    """
    - Open to admins.
    - Admins can set passwords of subordinate users.
    """

    @abstractmethod
    async def execute(self, command: SetUserPasswordCommand) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainTypeError:
        :raises UserNotFoundByIdError:
        :raises PasswordHasherBusyError:
        """
        pass
