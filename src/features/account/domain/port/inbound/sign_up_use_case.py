from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class SignUpCommand:
    username: str
    password: str


class SignUpResponse(TypedDict):
    id: UUID


class SignUpUseCase(ABC):
    """
    - Open to everyone.
    - Registers a new user with validation and uniqueness checks.
    - Passwords are peppered, salted, and stored as hashes.
    - A logged-in user cannot sign up until the session expires or is terminated.
    """

    @abstractmethod
    async def execute(self, command: SignUpCommand) -> SignUpResponse:
        """
        :raises AlreadyAuthenticatedError:
        :raises AuthorizationError:
        :raises DataMapperError:
        :raises DomainTypeError:
        :raises PasswordHasherBusyError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        pass
