import importlib
import logging
import pkgutil
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from shared.domain.domain_event import DomainEvent
from shared.domain.event_registry import (
    _event_type_registry,
    register_event,
)

log = logging.getLogger(__name__)

_registry: dict[type[DomainEvent], list[type]] = defaultdict(list)

__all__ = ["_event_type_registry", "register_event"]


def handles[T](*event_types: type[DomainEvent]) -> Callable[[type[T]], type[T]]:
    def decorator(cls: type[T]) -> type[T]:
        for event_type in event_types:
            _registry[event_type].append(cls)
            _event_type_registry[event_type.__name__] = event_type
            log.debug(
                "Registered handler %s for event %s", cls.__name__, event_type.__name__
            )
        return cls

    return decorator


def get_handlers_for(event_type: type[DomainEvent]) -> list[type]:
    return _registry.get(event_type, [])


def get_event_class(name: str) -> type[DomainEvent] | None:
    return _event_type_registry.get(name)


def auto_discover_handlers() -> None:
    handler_packages = [
        "account.infrastructure.events.handlers",
        "core.infrastructure.events.handlers",
    ]
    for package_name in handler_packages:
        try:
            handlers_package = importlib.import_module(package_name)
        except ModuleNotFoundError:
            log.debug("Handler package not found: %s", package_name)
            continue

        package_path: Any = handlers_package.__path__

        for module_info in pkgutil.walk_packages(
            package_path, prefix=f"{package_name}."
        ):
            importlib.import_module(module_info.name)
            log.debug("Auto-discovered handler module: %s", module_info.name)
