import importlib
import logging
import pkgutil
from collections import defaultdict
from typing import Any

from domain.shared.domain_event import DomainEvent

log = logging.getLogger(__name__)

_registry: dict[type[DomainEvent], list[type]] = defaultdict(list)


def handles(*event_types: type[DomainEvent]):
    def decorator[T](cls: type[T]) -> type[T]:
        for event_type in event_types:
            _registry[event_type].append(cls)
            log.debug("Registered handler %s for event %s", cls.__name__, event_type.__name__)
        return cls

    return decorator


def get_handlers_for(event_type: type[DomainEvent]) -> list[type]:
    return _registry.get(event_type, [])


def auto_discover_handlers() -> None:
    handlers_package = importlib.import_module("infrastructure.events.handlers")
    package_path: Any = handlers_package.__path__

    for module_info in pkgutil.walk_packages(package_path, prefix="infrastructure.events.handlers."):
        importlib.import_module(module_info.name)
        log.debug("Auto-discovered handler module: %s", module_info.name)
