from abc import abstractmethod
from typing import Protocol

from domain.user.value_objects import RawPassword, UserPasswordHash, UserId


class PasswordHasher(Protocol):
    @abstractmethod
    async def hash(self, raw_password: RawPassword) -> UserPasswordHash:
        """:raises PasswordHasherBusyError:"""

    @abstractmethod
    async def verify(
        self,
        raw_password: RawPassword,
        hashed_password: UserPasswordHash,
    ) -> bool:
        """:raises PasswordHasherBusyError:"""


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> UserId:
        """:raises AuthenticationError:"""


class AccessRevoker(Protocol):
    @abstractmethod
    async def remove_all_user_access(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""


class UserIdGenerator:
    @abstractmethod
    def generate(self) -> UserId: ...
