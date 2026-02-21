from dishka import Provider, Scope, provide, provide_all

from account.application.activate_account.handler import ActivateAccountHandler
from account.application.activate_account.port import ActivateAccountUseCase
from account.application.change_password.handler import ChangePasswordHandler
from account.application.change_password.port import ChangePasswordUseCase
from account.application.create_account.handler import CreateAccountHandler
from account.application.create_account.port import CreateAccountUseCase
from account.application.current_account.handler import CurrentAccountHandler
from account.application.current_account.port import CurrentAccountUseCase
from account.application.deactivate_account.handler import DeactivateAccountHandler
from account.application.deactivate_account.port import DeactivateAccountUseCase
from account.application.grant_admin.handler import GrantAdminHandler
from account.application.grant_admin.port import GrantAdminUseCase
from account.application.list_accounts.handler import ListAccountsHandler
from account.application.list_accounts.port import ListAccountsUseCase
from account.application.log_in.handler import LogInHandler
from account.application.log_in.port import LogInUseCase
from account.application.refresh_token.handler import RefreshTokenHandler
from account.application.refresh_token.port import RefreshTokenUseCase
from account.application.revoke_admin.handler import RevokeAdminHandler
from account.application.revoke_admin.port import RevokeAdminUseCase
from account.application.set_account_password.handler import SetAccountPasswordHandler
from account.application.set_account_password.port import SetAccountPasswordUseCase
from account.application.shared.account_unit_of_work import AccountUnitOfWork
from account.application.sign_up.handler import SignUpHandler
from account.application.sign_up.port import SignUpUseCase
from account.domain.account.ports import AccessRevoker
from account.domain.account.repository import AccountRepository
from account.infrastructure.persistence.sqla_account_repository import (
    SqlaAccountRepository,
)
from account.infrastructure.persistence.sqla_account_unit_of_work import (
    SqlaAccountUnitOfWork,
)
from account.infrastructure.security.access_revoker import RefreshTokenAccessRevoker
from core.application.create_profile.handler import CreateProfileHandler
from core.application.create_profile.port import CreateProfileUseCase
from core.application.get_my_profile.handler import GetMyProfileHandler
from core.application.get_my_profile.port import GetMyProfileUseCase
from core.application.list_profiles.handler import ListProfilesHandler
from core.application.list_profiles.port import ListProfilesUseCase
from core.application.set_username.handler import SetUsernameHandler
from core.application.set_username.port import SetUsernameUseCase
from core.application.shared.core_unit_of_work import CoreUnitOfWork
from core.application.update_profile.handler import UpdateProfileHandler
from core.application.update_profile.port import UpdateProfileUseCase
from core.domain.profile.repository import ProfileRepository
from core.infrastructure.persistence.sqla_core_unit_of_work import SqlaCoreUnitOfWork
from core.infrastructure.persistence.sqla_profile_repository import (
    SqlaProfileRepository,
)
from shared.application.event_dispatcher import EventDispatcher
from shared.domain.ports.identity_provider import IdentityProvider
from shared.infrastructure.events.dispatcher import OutboxEventDispatcher
from shared.infrastructure.persistence.types_ import MainAsyncSession
from shared.infrastructure.security.identity_provider import JwtBearerIdentityProvider


class AccountApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Concrete handler needed by other handlers as a direct dependency
    current_account_handler = provide_all(CurrentAccountHandler)

    # Ports Persistence
    account_unit_of_work = provide(SqlaAccountUnitOfWork, provides=AccountUnitOfWork)
    account_repository = provide(SqlaAccountRepository, provides=AccountRepository)

    # Ports Auth
    access_revoker = provide(RefreshTokenAccessRevoker, provides=AccessRevoker)
    identity_provider = provide(JwtBearerIdentityProvider, provides=IdentityProvider)

    @provide
    def event_dispatcher(self, session: MainAsyncSession) -> EventDispatcher:
        return OutboxEventDispatcher(session)

    # Account Use Cases
    activate_account_use_case = provide(
        ActivateAccountHandler, provides=ActivateAccountUseCase
    )
    create_account_use_case = provide(
        CreateAccountHandler, provides=CreateAccountUseCase
    )
    deactivate_account_use_case = provide(
        DeactivateAccountHandler, provides=DeactivateAccountUseCase
    )
    grant_admin_use_case = provide(GrantAdminHandler, provides=GrantAdminUseCase)
    revoke_admin_use_case = provide(RevokeAdminHandler, provides=RevokeAdminUseCase)
    set_account_password_use_case = provide(
        SetAccountPasswordHandler, provides=SetAccountPasswordUseCase
    )
    list_accounts_use_case = provide(ListAccountsHandler, provides=ListAccountsUseCase)
    current_account_use_case = provide(
        CurrentAccountHandler, provides=CurrentAccountUseCase
    )
    sign_up_use_case = provide(SignUpHandler, provides=SignUpUseCase)
    log_in_use_case = provide(LogInHandler, provides=LogInUseCase)
    refresh_token_use_case = provide(RefreshTokenHandler, provides=RefreshTokenUseCase)
    change_password_use_case = provide(
        ChangePasswordHandler, provides=ChangePasswordUseCase
    )


class CoreApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Ports Persistence
    core_unit_of_work = provide(SqlaCoreUnitOfWork, provides=CoreUnitOfWork)
    profile_repository = provide(SqlaProfileRepository, provides=ProfileRepository)

    # Core Use Cases
    create_profile_use_case = provide(
        CreateProfileHandler, provides=CreateProfileUseCase
    )
    get_my_profile_use_case = provide(GetMyProfileHandler, provides=GetMyProfileUseCase)
    set_username_use_case = provide(SetUsernameHandler, provides=SetUsernameUseCase)
    update_profile_use_case = provide(
        UpdateProfileHandler, provides=UpdateProfileUseCase
    )
    list_profiles_use_case = provide(ListProfilesHandler, provides=ListProfilesUseCase)
