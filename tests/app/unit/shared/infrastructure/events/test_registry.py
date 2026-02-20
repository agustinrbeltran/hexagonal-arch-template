from dataclasses import dataclass

import pytest

from shared.domain.domain_event import DomainEvent
from shared.infrastructure.events.registry import (
    _event_type_registry,
    _registry,
    get_event_class,
    get_handlers_for,
    handles,
)


@dataclass(frozen=True, kw_only=True)
class _TestEvent(DomainEvent):
    value: str


@dataclass(frozen=True, kw_only=True)
class _AnotherTestEvent(DomainEvent):
    count: int


@pytest.fixture(autouse=True)
def _clean_registries() -> None:
    # Save state
    saved_registry = dict(_registry)
    saved_type_registry = dict(_event_type_registry)

    yield  # type: ignore[misc]

    # Restore state
    _registry.clear()
    _registry.update(saved_registry)
    _event_type_registry.clear()
    _event_type_registry.update(saved_type_registry)


class TestHandlesDecorator:
    def test_registers_handler_for_event_type(self) -> None:
        @handles(_TestEvent)
        class MyHandler:
            pass

        assert MyHandler in get_handlers_for(_TestEvent)

    def test_registers_event_type_name(self) -> None:
        @handles(_TestEvent)
        class MyHandler:
            pass

        assert get_event_class("_TestEvent") is _TestEvent

    def test_multiple_event_types_registered(self) -> None:
        @handles(_TestEvent, _AnotherTestEvent)
        class MultiHandler:
            pass

        assert MultiHandler in get_handlers_for(_TestEvent)
        assert MultiHandler in get_handlers_for(_AnotherTestEvent)
        assert get_event_class("_TestEvent") is _TestEvent
        assert get_event_class("_AnotherTestEvent") is _AnotherTestEvent

    def test_multiple_handlers_for_same_event(self) -> None:
        @handles(_TestEvent)
        class HandlerA:
            pass

        @handles(_TestEvent)
        class HandlerB:
            pass

        handlers = get_handlers_for(_TestEvent)
        assert HandlerA in handlers
        assert HandlerB in handlers


class TestGetEventClass:
    def test_returns_registered_class(self) -> None:
        @handles(_TestEvent)
        class MyHandler:
            pass

        assert get_event_class("_TestEvent") is _TestEvent

    def test_returns_none_for_unknown(self) -> None:
        assert get_event_class("NonExistentEvent") is None


class TestGetHandlersFor:
    def test_returns_empty_for_unregistered_event(self) -> None:
        assert get_handlers_for(_AnotherTestEvent) == []
