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
from features.user.domain.core.vo.raw_password import RawPassword
from features.user.domain.core.vo.user_id import UserId
from features.user.domain.port.outbound.user_repository import UserRepository

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class SetUserPasswordCommand:
    user_id: UUID
    password: str


class SetUserPasswordUseCase:
    """
    - Open to admins.
    - Admins can set passwords of subordinate users.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_repository: UserRepository,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_repository = user_repository
        self._user_service = user_service
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: SetUserPasswordCommand) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainTypeError:
        :raises UserNotFoundByIdError:
        :raises PasswordHasherBusyError:
        """
        log.info(
            "Set user password: started. Target user ID: '%s'.",
            request_data.user_id,
        )

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )

        user_id = UserId(request_data.user_id)
        password = RawPassword(request_data.password)
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

        await self._user_service.change_password(user, password)
        await self._transaction_manager.commit()

        log.info("Set user password: done. Target user ID: '%s'.", user.id_.value)
