from abc import abstractmethod
from typing import Protocol

from shared.domain.domain_event import DomainEvent


class EventDispatcher(Protocol):
    @abstractmethod
    async def dispatch(self, events: list[DomainEvent]) -> None: ...
