from features.account.domain.core.services.auth_session_service import (
    AuthSessionService,
)
from features.user.domain.core.vo.user_id import UserId
from features.user.domain.port.outbound.identity_provider import IdentityProvider


class AuthSessionIdentityProvider(IdentityProvider):
    def __init__(self, auth_session_service: AuthSessionService) -> None:
        self._auth_session_service = auth_session_service

    async def get_current_user_id(self) -> UserId:
        """:raises AuthenticationError:"""
        return await self._auth_session_service.get_authenticated_user_id()
