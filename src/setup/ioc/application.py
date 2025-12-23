from dishka import Provider, Scope, provide, provide_all

from common.adapter.main_flusher_sqla import SqlaMainFlusher
from common.adapter.main_transaction_manager_sqla import SqlaMainTransactionManager
from common.domain.port.outbound.flusher import Flusher
from common.domain.port.outbound.transaction_manager import (
    TransactionManager,
)
from features.user.adapter.access_revoker import (
    AuthSessionAccessRevoker,
)
from features.user.adapter.identity_provider import (
    AuthSessionIdentityProvider,
)
from features.user.adapter.sqla_user_repository_adapter_ import (
    SqlaUserRepositoryAdapter,
)
from features.user.domain.core.service.activate_user_service import ActivateUserService
from features.user.domain.core.service.create_user_service import CreateUserService
from features.user.domain.core.service.current_user_service import CurrentUserService
from features.user.domain.core.service.deactivate_user_service import (
    DeactivateUserService,
)
from features.user.domain.core.service.grant_admin_service import GrantAdminService
from features.user.domain.core.service.list_users_service import ListUsersService
from features.user.domain.core.service.revoke_admin_service import RevokeAdminService
from features.user.domain.core.service.set_user_password_service import (
    SetUserPasswordService,
)
from features.user.domain.port.inbound.activate_user_use_case import ActivateUserUseCase
from features.user.domain.port.inbound.create_user_use_case import CreateUserUseCase
from features.user.domain.port.inbound.deactivate_user_use_case import (
    DeactivateUserUseCase,
)
from features.user.domain.port.inbound.grant_admin_use_case import GrantAdminUseCase
from features.user.domain.port.inbound.list_users_use_case import ListUsersUseCase
from features.user.domain.port.inbound.revoke_admin_use_case import RevokeAdminUseCase
from features.user.domain.port.inbound.set_user_password_use_case import (
    SetUserPasswordUseCase,
)
from features.user.domain.port.outbound.access_revoker import AccessRevoker
from features.user.domain.port.outbound.identity_provider import IdentityProvider
from features.user.domain.port.outbound.user_repository import UserRepository


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Services
    services = provide_all(
        CurrentUserService,
    )

    # Ports Persistence
    tx_manager = provide(SqlaMainTransactionManager, provides=TransactionManager)
    flusher = provide(SqlaMainFlusher, provides=Flusher)
    user_repository = provide(SqlaUserRepositoryAdapter, provides=UserRepository)

    # Ports Auth
    access_revoker = provide(AuthSessionAccessRevoker, provides=AccessRevoker)
    identity_provider = provide(AuthSessionIdentityProvider, provides=IdentityProvider)

    # Use Cases
    activate_user_use_case = provide(ActivateUserService, provides=ActivateUserUseCase)
    set_user_password_use_case = provide(
        SetUserPasswordService, provides=SetUserPasswordUseCase
    )
    create_user_use_case = provide(CreateUserService, provides=CreateUserUseCase)
    deactivate_user_use_case = provide(
        DeactivateUserService, provides=DeactivateUserUseCase
    )
    grant_admin_use_case = provide(GrantAdminService, provides=GrantAdminUseCase)
    revoke_admin_use_case = provide(RevokeAdminService, provides=RevokeAdminUseCase)

    # Queries
    list_users_use_case = provide(ListUsersService, provides=ListUsersUseCase)
