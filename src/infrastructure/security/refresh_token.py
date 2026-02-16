from dataclasses import dataclass
from datetime import datetime

from domain.user.value_objects import UserId


@dataclass(eq=False, kw_only=True)
class RefreshToken:
    id_: str
    user_id: UserId
    expiration: datetime
