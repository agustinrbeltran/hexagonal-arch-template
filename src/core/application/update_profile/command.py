from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateProfileCommand:
    first_name: str | None
    last_name: str | None
    birth_date: date | None
    username: str | None
