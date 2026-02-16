import logging

from application.create_user.command import CreateUserCommand, CreateUserResponse
from application.create_user.port import CreateUserUseCase
from application.current_user.handler import CurrentUserHandler
from application.shared.event_dispatcher import EventDispatcher
from application.shared.unit_of_work import UnitOfWork
from domain.user.errors import UsernameAlreadyExistsError
from domain.user.repository import UserRepository
from domain.user.services import (
    CanManageRole,
    RoleManagementContext,
    UserService,
    authorize,
)
from domain.user.value_objects import RawPassword, Username

log = logging.getLogger(__name__)


class CreateUserHandler(CreateUserUseCase):
    def __init__(
        self,
        current_user_handler: CurrentUserHandler,
        user_service: UserService,
        user_repository: UserRepository,
        unit_of_work: UnitOfWork,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self._current_user_handler = current_user_handler
        self._user_service = user_service
        self._user_repository = user_repository
        self._unit_of_work = unit_of_work
        self._event_dispatcher = event_dispatcher

    async def execute(self, command: CreateUserCommand) -> CreateUserResponse:
        log.info("Create user: started. Target username: '%s'.", command.username)

        current_user = await self._current_user_handler.get_current_user()

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
            await self._unit_of_work.commit()
        except UsernameAlreadyExistsError:
            raise

        await self._event_dispatcher.dispatch(user.collect_events())

        log.info("Create user: done. Target username: '%s'.", user.username.value)
        return CreateUserResponse(id=user.id_.value)
