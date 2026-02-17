from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class LogInCommand:
    username: str
    password: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LogInResult:
    access_token: str
    refresh_token: str
    expires_in: int
