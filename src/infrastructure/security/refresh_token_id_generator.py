import secrets

from domain.refresh_token.services import RefreshTokenIdGenerator


class StrRefreshTokenIdGenerator(RefreshTokenIdGenerator):
    def generate(self) -> str:
        return secrets.token_urlsafe(32)
