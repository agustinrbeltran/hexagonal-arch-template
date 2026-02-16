import secrets

from domain.auth_session.services import AuthSessionIdGenerator


class StrAuthSessionIdGenerator(AuthSessionIdGenerator):
    def generate(self) -> str:
        return secrets.token_urlsafe(32)
