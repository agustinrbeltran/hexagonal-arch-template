from domain.auth_session.services import AuthSessionService
from domain.user.ports import IdentityProvider
from domain.user.value_objects import UserId


class AuthSessionIdentityProvider(IdentityProvider):
    def __init__(self, auth_session_service: AuthSessionService) -> None:
        self._auth_session_service = auth_session_service

    async def get_current_user_id(self) -> UserId:
        """:raises AuthenticationError:"""
        return await self._auth_session_service.get_authenticated_user_id()
