import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from common.domain.port.outbound.flusher import Flusher
from common.domain.port.outbound.transaction_manager import (
    TransactionManager,
)
from features.user.domain.core.enums.user_role import UserRole
from features.user.domain.core.exceptions.user import UsernameAlreadyExistsError
from features.user.domain.core.service.current_user_service import CurrentUserService
from features.user.domain.core.service.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from features.user.domain.core.service.user_service import UserService
from features.user.domain.core.utils.authorize import authorize
from features.user.domain.core.vo.raw_password import RawPassword
from features.user.domain.core.vo.username import Username
from features.user.domain.port.outbound.user_repository import UserRepository

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserCommand:
    username: str
    password: str
    role: UserRole


class CreateUserResponse(TypedDict):
    id: UUID


class CreateUserUseCase:
    """
    - Open to admins.
    - Creates a new user, including admins, if the username is unique.
    - Only super admins can create new admins.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        user_repository: UserRepository,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._user_repository = user_repository
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, command: CreateUserCommand) -> CreateUserResponse:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainTypeError:
        :raises PasswordHasherBusyError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        log.info("Create user: started. Target username: '%s'.", command.username)

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=command.role,
            ),
        )

        username = Username(command.username)
        password = RawPassword(command.password)
        user = await self._user_service.create(username, password, command.role)

        self._user_repository.save(user)

        try:
            await self._flusher.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        log.info("Create user: done. Target username: '%s'.", user.username.value)
        return CreateUserResponse(id=user.id_.value)
