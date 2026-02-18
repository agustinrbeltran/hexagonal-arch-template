import logging

from domain.user.events import UserCreated
from infrastructure.events.registry import handles

log = logging.getLogger(__name__)


@handles(UserCreated)
class LogUserCreated:
    async def handle(self, event: UserCreated) -> None:
        log.info(
            "User created: id=%s, username=%s, role=%s",
            event.user_id,
            event.username,
            event.role,
        )
