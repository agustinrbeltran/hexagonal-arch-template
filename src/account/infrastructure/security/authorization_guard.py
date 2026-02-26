from account.domain.account.enums import AccountRole
from account.domain.account.repository import AccountRepository
from shared.domain.errors import AuthorizationError
from shared.domain.ports.identity_provider import IdentityProvider


class AccountAuthorizationGuard:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        account_repository: AccountRepository,
    ) -> None:
        self._identity_provider = identity_provider
        self._account_repository = account_repository

    async def require_admin(self) -> None:
        account_id = await self._identity_provider.get_current_account_id()
        account = await self._account_repository.get_by_id(account_id)
        if account is None or not account.is_active:
            raise AuthorizationError("Insufficient permissions.")
        if account.role not in {AccountRole.SUPER_ADMIN, AccountRole.ADMIN}:
            raise AuthorizationError("Insufficient permissions.")
