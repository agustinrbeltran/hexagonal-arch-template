from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangePasswordCommand:
    current_password: str
    new_password: str
