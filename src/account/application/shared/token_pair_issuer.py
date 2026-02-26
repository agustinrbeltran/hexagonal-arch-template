from abc import abstractmethod
from typing import Protocol

from account.domain.account.value_objects import Email, RawPassword


class TokenPairIssuer(Protocol):
    @property
    @abstractmethod
    def access_token_expiry_seconds(self) -> int: ...

    @abstractmethod
    async def issue_token_pair(
        self, email: Email, password: RawPassword
    ) -> tuple[str, str]:
        """:raises AuthenticationError:"""
