from abc import ABC, abstractmethod


class LogOutUseCase(ABC):
    """
    - Open to authenticated users.
    - Logs the user out by deleting the JWT access token from cookies
    and removing the session from the database.
    """

    @abstractmethod
    async def execute(self) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        pass
