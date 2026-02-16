from abc import abstractmethod
from typing import Protocol

from domain.user.value_objects import UserId


class TokenPairIssuer(Protocol):
    @property
    @abstractmethod
    def access_token_expiry_seconds(self) -> int: ...

    @abstractmethod
    def issue_token_pair(self, user_id: UserId) -> tuple[str, str]: ...
