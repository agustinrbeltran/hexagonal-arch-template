from dataclasses import dataclass
from datetime import datetime

from domain.user.value_objects import UserId


@dataclass(eq=False, kw_only=True)
class AuthSession:
    """
    AuthSession aggregate. References User by UserId only (no direct object reference).
    Currently a simple dataclass; can be promoted to AggregateRoot when
    domain event support is needed for session lifecycle.
    """

    id_: str
    user_id: UserId
    expiration: datetime
