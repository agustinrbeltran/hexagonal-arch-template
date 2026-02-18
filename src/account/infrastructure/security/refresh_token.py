from dataclasses import dataclass
from datetime import datetime

from shared.domain.account_id import AccountId


@dataclass(eq=False, kw_only=True)
class RefreshToken:
    id_: str
    account_id: AccountId
    expiration: datetime
