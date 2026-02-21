from dataclasses import dataclass, field
from datetime import date

from shared.domain.unset import UNSET, Unset


@dataclass(frozen=True, slots=True, kw_only=True)
class PatchProfileCommand:
    first_name: str | Unset | None = field(default=UNSET)
    last_name: str | Unset | None = field(default=UNSET)
    birth_date: date | Unset | None = field(default=UNSET)
    username: str | Unset | None = field(default=UNSET)
