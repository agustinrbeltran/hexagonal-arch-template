import logging

from shared.domain.domain_event import DomainEvent
from shared.infrastructure.events.serialization import serialize_event
from shared.infrastructure.persistence.mappers.outbox import OutboxRecord
from shared.infrastructure.persistence.types_ import MainAsyncSession

log = logging.getLogger(__name__)


class OutboxEventDispatcher:
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    async def dispatch(self, events: list[DomainEvent]) -> None:
        for event in events:
            log.debug(
                "Writing event to outbox: %s (id=%s)",
                event.event_type,
                event.event_id,
            )

            record = OutboxRecord(
                event_type=event.event_type,
                payload=serialize_event(event),
                occurred_at=event.occurred_at,
            )
            self._session.add(record)
