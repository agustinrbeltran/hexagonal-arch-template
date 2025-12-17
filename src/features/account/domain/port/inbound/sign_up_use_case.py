import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from common.domain.port.outbound.flusher import Flusher
from common.domain.port.outbound.transaction_manager import TransactionManager
from features.user.adapter.exceptions.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from features.user.domain.core.constants import AUTH_ALREADY_AUTHENTICATED
from features.user.domain.core.exceptions.user import UsernameAlreadyExistsError
from features.user.domain.core.service.current_user_service import CurrentUserService
from features.user.domain.core.service.user_service import UserService
from features.user.domain.core.vo.raw_password import RawPassword
from features.user.domain.core.vo.username import Username
from features.user.domain.port.outbound.user_repository import UserRepository

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class SignUpCommand:
    username: str
    password: str


class SignUpResponse(TypedDict):
    id: UUID


class SignUpUseCase:
    """
    - Open to everyone.
    - Registers a new user with validation and uniqueness checks.
    - Passwords are peppered, salted, and stored as hashes.
    - A logged-in user cannot sign up until the session expires or is terminated.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        user_command_gateway: UserRepository,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._user_command_gateway = user_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: SignUpCommand) -> SignUpResponse:
        """
        :raises AlreadyAuthenticatedError:
        :raises AuthorizationError:
        :raises DataMapperError:
        :raises DomainTypeError:
        :raises PasswordHasherBusyError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        log.info("Sign up: started. Username: '%s'.", request_data.username)

        try:
            await self._current_user_service.get_current_user()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except AuthenticationError:
            pass

        username = Username(request_data.username)
        password = RawPassword(request_data.password)

        user = await self._user_service.create_user(username, password)

        self._user_command_gateway.save(user)

        try:
            await self._flusher.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        log.info("Sign up: done. Username: '%s'.", user.username.value)
        return SignUpResponse(id=user.id_.value)
