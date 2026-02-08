import logging

from application.current_user.handler import CurrentUserHandler
from application.grant_admin.command import GrantAdminCommand
from application.grant_admin.port import GrantAdminUseCase
from application.shared.event_dispatcher import EventDispatcher
from application.shared.unit_of_work import UnitOfWork
from domain.user.entity import User
from domain.user.enums import UserRole
from domain.user.errors import UserNotFoundByIdError
from domain.user.repository import UserRepository
from domain.user.services import (
    CanManageRole,
    RoleManagementContext,
    authorize,
)
from domain.user.value_objects import UserId

log = logging.getLogger(__name__)


class GrantAdminHandler(GrantAdminUseCase):
    def __init__(
        self,
        current_user_handler: CurrentUserHandler,
        user_repository: UserRepository,
        unit_of_work: UnitOfWork,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self._current_user_handler = current_user_handler
        self._user_repository = user_repository
        self._unit_of_work = unit_of_work
        self._event_dispatcher = event_dispatcher

    async def execute(self, command: GrantAdminCommand) -> None:
        log.info("Grant admin: started. Target user ID: '%s'.", command.user_id)

        current_user = await self._current_user_handler.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.ADMIN,
            ),
        )

        user_id = UserId(command.user_id)
        user: User | None = await self._user_repository.get_by_id(
            user_id,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByIdError(user_id)

        if user.change_role(UserRole.ADMIN):
            await self._unit_of_work.commit()

        await self._event_dispatcher.dispatch(user.collect_events())

        log.info("Grant admin: done. Target user ID: '%s'.", user.id_.value)
