import asyncio
import contextlib
from dataclasses import dataclass
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from shared.domain.domain_event import DomainEvent
from shared.infrastructure.events.registry import (
    _event_type_registry,
    _registry,
)
from shared.infrastructure.events.relay import OutboxRelay
from shared.infrastructure.persistence.mappers.outbox import OutboxRecord


@dataclass(frozen=True, kw_only=True)
class _RelayTestEvent(DomainEvent):
    value: str


class _RelayTestHandler:
    def __init__(self) -> None:
        self.handled_events: list[DomainEvent] = []

    async def handle(self, event: _RelayTestEvent) -> None:
        self.handled_events.append(event)


class _FailingHandler:
    async def handle(self, event: _RelayTestEvent) -> None:
        msg = "Handler failure"
        raise RuntimeError(msg)


@pytest.fixture(autouse=True)
def _register_test_event():  # type: ignore[no-untyped-def]
    saved_registry = dict(_registry)
    saved_type_registry = dict(_event_type_registry)

    _event_type_registry["_RelayTestEvent"] = _RelayTestEvent
    _registry[_RelayTestEvent] = [_RelayTestHandler]

    yield

    _registry.clear()
    _registry.update(saved_registry)
    _event_type_registry.clear()
    _event_type_registry.update(saved_type_registry)


def _make_outbox_record(
    event_type: str = "_RelayTestEvent",
    payload: str = (
        '{"value": "test", "event_id": "abc",'
        ' "occurred_at": "2026-01-01T00:00:00+00:00"}'
    ),
    retry_count: int = 0,
) -> OutboxRecord:
    return OutboxRecord(
        id=uuid4(),
        event_type=event_type,
        payload=payload,
        occurred_at=datetime.now(UTC),
        delivered=False,
        retry_count=retry_count,
    )


def _make_mock_session(entries: list[OutboxRecord]) -> AsyncMock:
    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.fetchall.return_value = entries
    session.execute = AsyncMock(return_value=result_mock)
    session.commit = AsyncMock()
    return session


class _FakeSessionFactory:
    """Mimics async_sessionmaker.__call__() returning an async context manager."""

    def __init__(self, session: AsyncMock) -> None:
        self._session = session

    def __call__(self) -> "_FakeSessionFactory":
        return self

    async def __aenter__(self) -> AsyncMock:
        return self._session

    async def __aexit__(self, *args: object) -> None:
        pass


class _FakeContainer:
    """Mimics Dishka container scope creation."""

    def __init__(self, child: AsyncMock) -> None:
        self._child = child

    def __call__(self, **kwargs: object) -> "_FakeContainer":
        return self

    async def __aenter__(self) -> AsyncMock:
        return self._child

    async def __aexit__(self, *args: object) -> None:
        pass


def _make_relay(
    container: object,
    session_factory: object,
    max_retries: int = 3,
) -> OutboxRelay:
    return OutboxRelay(
        container=container,  # type: ignore[arg-type]
        session_factory=session_factory,  # type: ignore[arg-type]
        poll_interval=0.01,
        max_retries=max_retries,
    )


@pytest.mark.asyncio
async def test_processes_undelivered_entry() -> None:
    entry = _make_outbox_record()
    session = _make_mock_session([entry])
    session_factory = _FakeSessionFactory(session)

    handler_instance = _RelayTestHandler()
    child_scope = AsyncMock()
    child_scope.get = AsyncMock(return_value=handler_instance)
    container = _FakeContainer(child_scope)

    relay = _make_relay(container, session_factory)
    await relay._poll()

    assert len(handler_instance.handled_events) == 1
    # Select + update
    assert session.execute.call_count == 2
    session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_no_entries_skips_processing() -> None:
    session = _make_mock_session([])
    session_factory = _FakeSessionFactory(session)
    container = _FakeContainer(AsyncMock())

    relay = _make_relay(container, session_factory)
    await relay._poll()

    # Only the select query
    assert session.execute.call_count == 1
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_handler_failure_increments_retry() -> None:
    entry = _make_outbox_record(retry_count=0)
    session = _make_mock_session([entry])
    session_factory = _FakeSessionFactory(session)

    _registry[_RelayTestEvent] = [_FailingHandler]

    failing_handler = _FailingHandler()
    child_scope = AsyncMock()
    child_scope.get = AsyncMock(return_value=failing_handler)
    container = _FakeContainer(child_scope)

    relay = _make_relay(container, session_factory)
    await relay._poll()

    # Select + retry update
    assert session.execute.call_count == 2
    session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_graceful_shutdown_on_cancel() -> None:
    session = _make_mock_session([])
    session_factory = _FakeSessionFactory(session)
    container = _FakeContainer(AsyncMock())

    relay = _make_relay(container, session_factory)

    task = asyncio.create_task(relay.run())
    await asyncio.sleep(0.05)
    task.cancel()

    # Should not raise, just exit cleanly
    with contextlib.suppress(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_no_handlers_marks_delivered() -> None:
    entry = _make_outbox_record()
    session = _make_mock_session([entry])
    session_factory = _FakeSessionFactory(session)

    _registry[_RelayTestEvent] = []

    container = _FakeContainer(AsyncMock())

    relay = _make_relay(container, session_factory)
    await relay._poll()

    # Select + update (mark delivered)
    assert session.execute.call_count == 2
    session.commit.assert_awaited()
