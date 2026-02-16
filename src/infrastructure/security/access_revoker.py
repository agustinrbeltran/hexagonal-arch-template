from domain.refresh_token.services import RefreshTokenService
from domain.user.ports import AccessRevoker
from domain.user.value_objects import UserId


class RefreshTokenAccessRevoker(AccessRevoker):
    def __init__(self, refresh_token_service: RefreshTokenService) -> None:
        self._refresh_token_service = refresh_token_service

    async def remove_all_user_access(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""
        await self._refresh_token_service.revoke_all_for_user(user_id)
