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
    RoleManagementContext,
)
from features.user.domain.core.service.user_service import UserService
from features.user.domain.core.utils.authorize import authorize
from features.user.domain.core.vo.user_id import UserId
from features.user.domain.port.outbound.user_repository import UserRepository

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GrantAdminCommand:
    user_id: UUID


class GrantAdminUseCase:
    """
    - Open to super admins.
    - Grants admin rights to a specified user.
    - Super admin rights cannot be changed.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_command_gateway: UserRepository,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_command_gateway = user_command_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: GrantAdminCommand) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises UserNotFoundByIdError:
        :raises RoleChangeNotPermittedError:
        """
        log.info("Grant admin: started. Target user ID: '%s'.", request_data.user_id)

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.ADMIN,
            ),
        )

        user_id = UserId(request_data.user_id)
        user: User | None = await self._user_command_gateway.get_by_id(
            user_id,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByIdError(user_id)

        if self._user_service.toggle_user_admin_role(user, is_admin=True):
            await self._transaction_manager.commit()

        log.info("Grant admin: done. Target user ID: '%s'.", user.id_.value)
