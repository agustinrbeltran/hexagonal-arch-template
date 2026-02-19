from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class RefreshTokenCommand:
    refresh_token: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RefreshTokenResult:
    access_token: str
    refresh_token: str
    expires_in: int
