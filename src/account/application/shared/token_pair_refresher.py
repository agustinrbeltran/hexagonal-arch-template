from abc import abstractmethod
from typing import Protocol


class TokenPairRefresher(Protocol):
    @property
    @abstractmethod
    def access_token_expiry_seconds(self) -> int: ...

    @abstractmethod
    async def refresh(self, refresh_token_id: str) -> tuple[str, str]: ...
