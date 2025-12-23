from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangePasswordCommand:
    current_password: str
    new_password: str


class ChangePasswordUseCase(ABC):
    """
    - Open to authenticated users.
    - The current user can change their password.
    - New password must differ from current password.
    """

    @abstractmethod
    async def execute(self, command: ChangePasswordCommand) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainTypeError:
        :raises AuthenticationChangeError:
        :raises ReAuthenticationError:
        :raises PasswordHasherBusyError:
        """
        pass
