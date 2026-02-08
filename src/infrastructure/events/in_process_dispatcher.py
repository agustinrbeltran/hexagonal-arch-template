import logging

from domain.shared.domain_event import DomainEvent

log = logging.getLogger(__name__)


class InProcessEventDispatcher:
    async def dispatch(self, events: list[DomainEvent]) -> None:
        for event in events:
            log.debug(
                "Dispatching domain event: %s (id=%s)",
                event.event_type,
                event.event_id,
            )
