from dataclasses import dataclass
from datetime import datetime

from features.user.domain.core.vo.user_id import UserId


@dataclass(eq=False, kw_only=True)
class AuthSession:
    """
    This class can become a domain entity in a new bounded context, enabling
    a monolithic architecture to become modular, while the other classes working
    with it are likely to become application and infrastructure layer components.

    For example, `LogInHandler` can become an interactor.
    """

    id_: str
    user_id: UserId
    expiration: datetime
