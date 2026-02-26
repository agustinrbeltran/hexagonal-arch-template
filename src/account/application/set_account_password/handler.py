import logging

from account.application.current_account.port import CurrentAccountUseCase
from account.application.set_account_password.command import SetAccountPasswordCommand
from account.application.set_account_password.port import SetAccountPasswordUseCase
from account.application.shared.password_resetter import PasswordResetter
from account.domain.account.entity import Account
from account.domain.account.enums import AccountRole
from account.domain.account.errors import AccountNotFoundByIdError
from account.domain.account.repository import AccountRepository
from account.domain.account.services import (
    AccountManagementContext,
    CanManageRole,
    CanManageSubordinate,
    RoleManagementContext,
    authorize,
)
from account.domain.account.value_objects import RawPassword
from shared.domain.account_id import AccountId

log = logging.getLogger(__name__)


class SetAccountPasswordHandler(SetAccountPasswordUseCase):
    def __init__(
        self,
        current_account_handler: CurrentAccountUseCase,
        account_repository: AccountRepository,
        password_resetter: PasswordResetter,
    ) -> None:
        self._current_account_handler = current_account_handler
        self._account_repository = account_repository
        self._password_resetter = password_resetter

    async def execute(self, command: SetAccountPasswordCommand) -> None:
        log.info(
            "Set account password: started. Target account ID: '%s'.",
            command.account_id,
        )

        current_account = await self._current_account_handler.get_current_account()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_account,
                target_role=AccountRole.USER,
            ),
        )

        account_id = AccountId(command.account_id)
        password = RawPassword(command.password)
        account: Account | None = await self._account_repository.get_by_id(
            account_id,
        )
        if account is None:
            raise AccountNotFoundByIdError(account_id)

        authorize(
            CanManageSubordinate(),
            context=AccountManagementContext(
                subject=current_account,
                target=account,
            ),
        )

        await self._password_resetter.reset_password(account_id, password)

        log.info(
            "Set account password: done. Target account ID: '%s'.",
            account.id_.value,
        )
