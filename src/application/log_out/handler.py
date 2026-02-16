import logging

from application.current_user.handler import CurrentUserHandler
from application.log_out.port import LogOutUseCase
from domain.auth_session.services import AuthSessionService

log = logging.getLogger(__name__)


class LogOutHandler(LogOutUseCase):
    def __init__(
        self,
        current_user_handler: CurrentUserHandler,
        auth_session_service: AuthSessionService,
    ) -> None:
        self._current_user_handler = current_user_handler
        self._auth_session_service = auth_session_service

    async def execute(self) -> None:
        log.info("Log out: started for unknown user.")

        current_user = await self._current_user_handler.get_current_user()

        log.info("Log out: user identified. User ID: '%s'.", current_user.id_)

        await self._auth_session_service.terminate_current_session()

        log.info("Log out: done. User ID: '%s'.", current_user.id_)
