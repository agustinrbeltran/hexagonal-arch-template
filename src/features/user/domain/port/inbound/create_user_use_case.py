from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from features.user.domain.core.enums.user_role import UserRole


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserCommand:
    username: str
    password: str
    role: UserRole


class CreateUserResponse(TypedDict):
    id: UUID


class CreateUserUseCase(ABC):
    """
    - Open to admins.
    - Creates a new user, including admins, if the username is unique.
    - Only super admins can create new admins.
    """

    @abstractmethod
    async def execute(self, command: CreateUserCommand) -> CreateUserResponse:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainTypeError:
        :raises PasswordHasherBusyError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        pass
