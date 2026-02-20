import logging

from account.application.create_account.command import (
    CreateAccountCommand,
    CreateAccountResponse,
)
from account.application.create_account.port import CreateAccountUseCase
from account.application.current_account.handler import CurrentAccountHandler
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.domain.account.errors import EmailAlreadyExistsError
from account.domain.account.repository import AccountRepository
from account.domain.account.services import (
    AccountService,
    CanManageRole,
    RoleManagementContext,
    authorize,
)
from account.domain.account.value_objects import Email, RawPassword
from shared.application.event_dispatcher import EventDispatcher

log = logging.getLogger(__name__)


class CreateAccountHandler(CreateAccountUseCase):
    def __init__(
        self,
        current_account_handler: CurrentAccountHandler,
        account_service: AccountService,
        account_repository: AccountRepository,
        account_unit_of_work: AccountUnitOfWork,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self._current_account_handler = current_account_handler
        self._account_service = account_service
        self._account_repository = account_repository
        self._account_unit_of_work = account_unit_of_work
        self._event_dispatcher = event_dispatcher

    async def execute(self, command: CreateAccountCommand) -> CreateAccountResponse:
        log.info("Create account: started. Target email: '%s'.", command.email)

        current_account = await self._current_account_handler.get_current_account()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_account,
                target_role=command.role,
            ),
        )

        email = Email(command.email)
        password = RawPassword(command.password)
        account = await self._account_service.create(email, password, command.role)

        self._account_repository.save(account)

        await self._event_dispatcher.dispatch(account.collect_events())

        try:
            await self._account_unit_of_work.commit()
        except EmailAlreadyExistsError:
            raise

        log.info("Create account: done. Target email: '%s'.", account.email.value)
        return CreateAccountResponse(id=account.id_.value)
