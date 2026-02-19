import logging

from account.domain.account.events import AccountCreated
from shared.infrastructure.events.registry import handles

log = logging.getLogger(__name__)


@handles(AccountCreated)
class LogAccountCreated:
    async def handle(self, event: AccountCreated) -> None:
        log.info(
            "Account created: id=%s, email=%s, role=%s",
            event.account_id,
            event.email,
            event.role,
        )
