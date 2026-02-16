from domain.auth_session.services import AuthSessionService
from domain.user.ports import AccessRevoker
from domain.user.value_objects import UserId


class AuthSessionAccessRevoker(AccessRevoker):
    def __init__(self, auth_session_service: AuthSessionService) -> None:
        self._auth_session_service = auth_session_service

    async def remove_all_user_access(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""
        await self._auth_session_service.terminate_all_sessions_for_user(user_id)
