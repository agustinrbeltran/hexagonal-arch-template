import logging

from shared.domain.domain_event import DomainEvent

log = logging.getLogger(__name__)

_event_type_registry: dict[str, type[DomainEvent]] = {}


def register_event[T: DomainEvent](cls: type[T]) -> type[T]:
    _event_type_registry[cls.__name__] = cls
    log.debug("Registered event type %s", cls.__name__)
    return cls
