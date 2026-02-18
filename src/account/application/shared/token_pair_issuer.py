from abc import abstractmethod
from typing import Protocol

from shared.domain.account_id import AccountId


class TokenPairIssuer(Protocol):
    @property
    @abstractmethod
    def access_token_expiry_seconds(self) -> int: ...

    @abstractmethod
    def issue_token_pair(self, account_id: AccountId) -> tuple[str, str]: ...
