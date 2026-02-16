from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CurrentUserQuery:
    for_update: bool = False
