import logging
from typing import Final

from account.application.current_account.port import CurrentAccountUseCase
from account.domain.account.entity import Account
from account.domain.account.ports import AccessRevoker
from account.domain.account.repository import AccountRepository
from shared.domain.errors import AuthorizationError
from shared.domain.ports.identity_provider import IdentityProvider

log = logging.getLogger(__name__)

AUTHZ_NOT_AUTHORIZED: Final[str] = "Not authorized."
AUTHZ_NO_CURRENT_ACCOUNT: Final[str] = (
    "Failed to retrieve current account. Removing all access."
)


class CurrentAccountHandler(CurrentAccountUseCase):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        account_repository: AccountRepository,
        access_revoker: AccessRevoker,
    ) -> None:
        self._identity_provider = identity_provider
        self._account_repository = account_repository
        self._access_revoker = access_revoker

    async def get_current_account(self, for_update: bool = False) -> Account:
        current_account_id = await self._identity_provider.get_current_account_id()
        account: Account | None = await self._account_repository.get_by_id(
            current_account_id,
            for_update=for_update,
        )
        if account is None or not account.is_active:
            log.warning("%s ID: %s.", AUTHZ_NO_CURRENT_ACCOUNT, current_account_id)
            await self._access_revoker.remove_all_account_access(current_account_id)
            raise AuthorizationError(AUTHZ_NOT_AUTHORIZED)

        return account
