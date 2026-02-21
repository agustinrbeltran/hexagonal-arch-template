from dataclasses import dataclass, field
from datetime import date

from shared.domain.unset import UNSET, _Unset


@dataclass(frozen=True, slots=True, kw_only=True)
class PatchProfileCommand:
    first_name: str | None | _Unset = field(default=UNSET)
    last_name: str | None | _Unset = field(default=UNSET)
    birth_date: date | None | _Unset = field(default=UNSET)
    username: str | None | _Unset = field(default=UNSET)
