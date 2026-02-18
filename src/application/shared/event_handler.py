from typing import Protocol, runtime_checkable

from domain.shared.domain_event import DomainEvent


@runtime_checkable
class EventHandler[E: DomainEvent](Protocol):
    async def handle(self, event: E) -> None: ...
