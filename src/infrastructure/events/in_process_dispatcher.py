import asyncio
import logging

from dishka import AsyncContainer

from domain.shared.domain_event import DomainEvent
from infrastructure.events.registry import get_handlers_for

log = logging.getLogger(__name__)


class InProcessEventDispatcher:
    def __init__(self, container: AsyncContainer) -> None:
        self._container = container

    async def dispatch(self, events: list[DomainEvent]) -> None:
        for event in events:
            log.debug(
                "Dispatching domain event: %s (id=%s)",
                event.event_type,
                event.event_id,
            )

            handler_types = get_handlers_for(type(event))
            if not handler_types:
                continue

            tasks = []
            for handler_type in handler_types:
                try:
                    handler = await self._container.get(handler_type)
                    tasks.append(handler.handle(event))
                except Exception:
                    log.exception("Failed to resolve handler %s", handler_type.__name__)

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, BaseException):
                        log.exception(
                            "Handler error for event %s (id=%s)",
                            event.event_type,
                            event.event_id,
                            exc_info=result,
                        )
