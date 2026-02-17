from typing import Any, Self

from domain.shared.domain_event import DomainEvent
from domain.shared.entity import Entity
from domain.shared.value_object import ValueObject


class AggregateRoot[T: ValueObject](Entity[T]):
    _events: list[DomainEvent]

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is AggregateRoot:
            raise TypeError("Base AggregateRoot cannot be instantiated directly.")
        return object.__new__(cls)

    def __init__(self, *, id_: T) -> None:
        super().__init__(id_=id_)
        self._events = []

    def _register_event(self, event: DomainEvent) -> None:
        try:
            self._events.append(event)
        except AttributeError:
            self._events = [event]

    def collect_events(self) -> list[DomainEvent]:
        try:
            events = list(self._events)
            self._events.clear()
        except AttributeError:
            self._events = []
            events = []
        return events
