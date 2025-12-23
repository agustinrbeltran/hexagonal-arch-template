from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class LogInCommand:
    username: str
    password: str


class LogInUseCase(ABC):
    """
    - Open to everyone.
    - Authenticates registered user,
    sets a JWT access token with a session ID in cookies,
    and creates a session.
    - A logged-in user cannot log in again
    until the session expires or is terminated.
    - Authentication renews automatically
    when accessing protected routes before expiration.
    - If the JWT is invalid, expired, or the session is terminated,
    the user loses authentication.
    """

    @abstractmethod
    async def execute(self, command: LogInCommand) -> None:
        """
        :raises AlreadyAuthenticatedError:
        :raises AuthorizationError:
        :raises DataMapperError:
        :raises DomainTypeError:
        :raises UserNotFoundByUsernameError:
        :raises PasswordHasherBusyError:
        :raises AuthenticationError:
        """
        pass
