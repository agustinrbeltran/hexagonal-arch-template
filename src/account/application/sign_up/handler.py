import logging
from typing import Final

from account.application.current_account.port import CurrentAccountUseCase
from account.application.shared.account_provisioner import AccountProvisioner
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.application.sign_up.command import SignUpCommand, SignUpResponse
from account.application.sign_up.port import SignUpUseCase
from account.domain.account.entity import Account
from account.domain.account.errors import EmailAlreadyExistsError
from account.domain.account.repository import AccountRepository
from account.domain.account.value_objects import Email, RawPassword
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.errors import AuthorizationError

log = logging.getLogger(__name__)

AUTH_ALREADY_AUTHENTICATED: Final[str] = (
    "You are already authenticated. Consider logging out."
)


class AlreadyAuthenticatedError(Exception):
    pass


class SignUpHandler(SignUpUseCase):
    def __init__(
        self,
        current_account_handler: CurrentAccountUseCase,
        account_provisioner: AccountProvisioner,
        account_repository: AccountRepository,
        account_unit_of_work: AccountUnitOfWork,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self._current_account_handler = current_account_handler
        self._account_provisioner = account_provisioner
        self._account_repository = account_repository
        self._account_unit_of_work = account_unit_of_work
        self._event_dispatcher = event_dispatcher

    async def execute(self, command: SignUpCommand) -> SignUpResponse:
        log.info("Sign up: started. Email: '%s'.", command.email)

        try:
            await self._current_account_handler.get_current_account()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except (AuthorizationError, Exception) as err:
            if isinstance(err, AlreadyAuthenticatedError):
                raise
            # Not authenticated — proceed with sign-up
            pass

        email = Email(command.email)
        password = RawPassword(command.password)

        account_id = await self._account_provisioner.register(email, password)

        account = Account.create(id_=account_id, email=email)

        await self._account_repository.save(account)

        await self._event_dispatcher.dispatch(account.collect_events())

        try:
            await self._account_unit_of_work.commit()
        except EmailAlreadyExistsError:
            raise

        log.info("Sign up: done. Email: '%s'.", account.email.value)
        return SignUpResponse(id=account.id_.value)
