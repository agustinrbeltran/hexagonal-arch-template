from account.domain.account.ports import AccessRevoker
from account.infrastructure.security.refresh_token_service import RefreshTokenService
from shared.domain.account_id import AccountId


class RefreshTokenAccessRevoker(AccessRevoker):
    def __init__(self, refresh_token_service: RefreshTokenService) -> None:
        self._refresh_token_service = refresh_token_service

    async def remove_all_account_access(self, account_id: AccountId) -> None:
        """:raises DataMapperError:"""
        await self._refresh_token_service.revoke_all_for_account(account_id)
