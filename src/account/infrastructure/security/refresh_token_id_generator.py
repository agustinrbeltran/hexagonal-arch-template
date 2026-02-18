import secrets

from account.infrastructure.security.refresh_token_service import RefreshTokenIdGenerator


class StrRefreshTokenIdGenerator(RefreshTokenIdGenerator):
    def generate(self) -> str:
        return secrets.token_urlsafe(32)
