import asyncio
import logging
from datetime import UTC, datetime

from dishka import AsyncContainer, Scope
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.application.event_handler import EventHandler
from shared.domain.domain_event import DomainEvent
from shared.infrastructure.events.registry import get_handlers_for
from shared.infrastructure.events.serialization import deserialize_event
from shared.infrastructure.persistence.mappers.outbox import OutboxRecord, outbox_table

log = logging.getLogger(__name__)

DEFAULT_POLL_INTERVAL: float = 30.0
DEFAULT_MAX_RETRIES: int = 5


class OutboxRelay:
    def __init__(
        self,
        container: AsyncContainer,
        session_factory: async_sessionmaker[AsyncSession],
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._container = container
        self._session_factory = session_factory
        self._poll_interval = poll_interval
        self._max_retries = max_retries

    async def run(self) -> None:
        log.info("Outbox relay started (poll_interval=%.1fs).", self._poll_interval)
        try:
            while True:
                await self._poll()
                await asyncio.sleep(self._poll_interval)
        except asyncio.CancelledError:
            log.info("Outbox relay shutting down gracefully.")

    async def _poll(self) -> None:
        async with self._session_factory() as session:
            stmt = (
                select(outbox_table)
                .where(
                    outbox_table.c.delivered.is_(False),
                    outbox_table.c.retry_count < self._max_retries,
                )
                .order_by(outbox_table.c.occurred_at)
            )
            result = await session.execute(stmt)
            rows = result.fetchall()
            entries = [
                OutboxRecord(
                    id=row.id,
                    event_type=row.event_type,
                    payload=row.payload,
                    occurred_at=row.occurred_at,
                    delivered=row.delivered,
                    delivered_at=row.delivered_at,
                    retry_count=row.retry_count,
                )
                for row in rows
            ]

            if not entries:
                return

            log.debug("Outbox relay: processing %d entries.", len(entries))

            for entry in entries:
                await self._process_entry(entry, session)

    async def _process_entry(self, entry: OutboxRecord, session: AsyncSession) -> None:
        try:
            event = deserialize_event(entry.event_type, entry.payload)
        except Exception:
            log.exception(
                "Failed to deserialize outbox entry %s (type=%s). Incrementing retry.",
                entry.id,
                entry.event_type,
            )
            await self._increment_retry(entry, session)
            return

        handler_types = get_handlers_for(type(event))

        any_failed = False
        for handler_type in handler_types:
            try:
                await self._execute_handler(handler_type, event)
            except Exception:
                log.exception(
                    "Handler %s failed for event %s (id=%s).",
                    handler_type.__name__,
                    entry.event_type,
                    entry.id,
                )
                any_failed = True

        if any_failed:
            await self._increment_retry(entry, session)
        else:
            await self._mark_delivered(entry, session)

    async def _execute_handler(self, handler_type: type, event: DomainEvent) -> None:
        async with self._container(scope=Scope.REQUEST) as child:
            handler: EventHandler[DomainEvent] = await child.get(handler_type)
            await handler.handle(event)

    async def _mark_delivered(self, entry: OutboxRecord, session: AsyncSession) -> None:
        stmt = (
            update(outbox_table)
            .where(outbox_table.c.id == entry.id)
            .values(delivered=True, delivered_at=datetime.now(UTC))
        )
        await session.execute(stmt)
        await session.commit()
        log.debug("Outbox entry %s delivered.", entry.id)

    async def _increment_retry(
        self, entry: OutboxRecord, session: AsyncSession
    ) -> None:
        new_count = entry.retry_count + 1
        stmt = (
            update(outbox_table)
            .where(outbox_table.c.id == entry.id)
            .values(retry_count=new_count)
        )
        await session.execute(stmt)
        await session.commit()

        if new_count >= self._max_retries:
            log.critical(
                "Outbox entry %s (type=%s) reached max retries (%d). Giving up.",
                entry.id,
                entry.event_type,
                self._max_retries,
            )
        else:
            log.warning(
                "Outbox entry %s (type=%s) retry_count=%d.",
                entry.id,
                entry.event_type,
                new_count,
            )
