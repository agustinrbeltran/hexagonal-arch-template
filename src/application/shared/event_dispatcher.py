from abc import abstractmethod
from typing import Protocol

from domain.shared.domain_event import DomainEvent


class EventDispatcher(Protocol):
    @abstractmethod
    async def dispatch(self, events: list[DomainEvent]) -> None: ...
