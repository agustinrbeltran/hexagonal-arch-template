import logging
from typing import Final

from application.current_user.port import CurrentUserUseCase
from domain.shared.errors import AuthorizationError
from domain.user.entity import User
from domain.user.ports import AccessRevoker, IdentityProvider
from domain.user.repository import UserRepository

log = logging.getLogger(__name__)

AUTHZ_NOT_AUTHORIZED: Final[str] = "Not authorized."
AUTHZ_NO_CURRENT_USER: Final[str] = (
    "Failed to retrieve current user. Removing all access."
)


class CurrentUserHandler(CurrentUserUseCase):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_repository: UserRepository,
        access_revoker: AccessRevoker,
    ) -> None:
        self._identity_provider = identity_provider
        self._user_repository = user_repository
        self._access_revoker = access_revoker

    async def get_current_user(self, for_update: bool = False) -> User:
        current_user_id = await self._identity_provider.get_current_user_id()
        user: User | None = await self._user_repository.get_by_id(
            current_user_id,
            for_update=for_update,
        )
        if user is None or not user.is_active:
            log.warning("%s ID: %s.", AUTHZ_NO_CURRENT_USER, current_user_id)
            await self._access_revoker.remove_all_user_access(current_user_id)
            raise AuthorizationError(AUTHZ_NOT_AUTHORIZED)

        return user
