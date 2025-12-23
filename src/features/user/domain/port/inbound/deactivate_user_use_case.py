import logging
from dataclasses import dataclass
from uuid import UUID

from common.domain.port.outbound.transaction_manager import (
    TransactionManager,
)
from features.user.domain.core.entities.user import User
from features.user.domain.core.enums.user_role import UserRole
from features.user.domain.core.exceptions.user import (
    UserNotFoundByIdError,
)
from features.user.domain.core.service.current_user_service import CurrentUserService
from features.user.domain.core.service.permissions import (
    CanManageRole,
    CanManageSubordinate,
    RoleManagementContext,
    UserManagementContext,
)
from features.user.domain.core.service.user_service import UserService
from features.user.domain.core.utils.authorize import authorize
from features.user.domain.core.vo.user_id import UserId
from features.user.domain.port.outbound.access_revoker import AccessRevoker
from features.user.domain.port.outbound.user_repository import UserRepository

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DeactivateUserCommand:
    user_id: UUID


class DeactivateUserUseCase:
    """
    - Open to admins.
    - Soft-deletes an existing user, making that user inactive.
    - Also deletes the user's sessions.
    - Only super admins can deactivate other admins.
    - Super admins cannot be soft-deleted.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_repository: UserRepository,
        user_service: UserService,
        transaction_manager: TransactionManager,
        access_revoker: AccessRevoker,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_repository = user_repository
        self._user_service = user_service
        self._transaction_manager = transaction_manager
        self._access_revoker = access_revoker

    async def execute(self, command: DeactivateUserCommand) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises UserNotFoundByIdError:
        :raises ActivationChangeNotPermittedError:
        """
        log.info(
            "Deactivate user: started. Target user ID: '%s'.",
            command.user_id,
        )

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )

        user_id = UserId(command.user_id)
        user: User | None = await self._user_repository.get_by_id(
            user_id,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByIdError(user_id)

        authorize(
            CanManageSubordinate(),
            context=UserManagementContext(
                subject=current_user,
                target=user,
            ),
        )

        if self._user_service.toggle_user_activation(user, is_active=False):
            await self._transaction_manager.commit()

        await self._access_revoker.remove_all_user_access(user.id_)

        log.info("Deactivate user: done. Target user ID: '%s'.", user.id_.value)
