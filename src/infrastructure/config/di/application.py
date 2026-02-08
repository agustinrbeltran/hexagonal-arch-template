from dishka import Provider, Scope, provide

from application.activate_user.handler import ActivateUserHandler
from application.activate_user.port import ActivateUserUseCase
from application.change_password.handler import ChangePasswordHandler
from application.change_password.port import ChangePasswordUseCase
from application.create_user.handler import CreateUserHandler
from application.create_user.port import CreateUserUseCase
from application.current_user.handler import CurrentUserHandler
from application.current_user.port import CurrentUserUseCase
from application.deactivate_user.handler import DeactivateUserHandler
from application.deactivate_user.port import DeactivateUserUseCase
from application.grant_admin.handler import GrantAdminHandler
from application.grant_admin.port import GrantAdminUseCase
from application.list_users.handler import ListUsersHandler
from application.list_users.port import ListUsersUseCase
from application.log_in.handler import LogInHandler
from application.log_in.port import LogInUseCase
from application.log_out.handler import LogOutHandler
from application.log_out.port import LogOutUseCase
from application.revoke_admin.handler import RevokeAdminHandler
from application.revoke_admin.port import RevokeAdminUseCase
from application.set_user_password.handler import SetUserPasswordHandler
from application.set_user_password.port import SetUserPasswordUseCase
from application.shared.event_dispatcher import EventDispatcher
from application.shared.unit_of_work import UnitOfWork
from application.sign_up.handler import SignUpHandler
from application.sign_up.port import SignUpUseCase
from domain.user.ports import AccessRevoker, IdentityProvider
from domain.user.repository import UserRepository
from infrastructure.events.in_process_dispatcher import InProcessEventDispatcher
from infrastructure.persistence.sqla_unit_of_work import SqlaUnitOfWork
from infrastructure.persistence.sqla_user_repository import SqlaUserRepository
from infrastructure.security.access_revoker import AuthSessionAccessRevoker
from infrastructure.security.identity_provider import AuthSessionIdentityProvider


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Ports Persistence
    unit_of_work = provide(SqlaUnitOfWork, provides=UnitOfWork)
    user_repository = provide(SqlaUserRepository, provides=UserRepository)
    event_dispatcher = provide(InProcessEventDispatcher, provides=EventDispatcher)

    # Ports Auth
    access_revoker = provide(AuthSessionAccessRevoker, provides=AccessRevoker)
    identity_provider = provide(AuthSessionIdentityProvider, provides=IdentityProvider)

    # User Use Cases
    activate_user_use_case = provide(ActivateUserHandler, provides=ActivateUserUseCase)
    create_user_use_case = provide(CreateUserHandler, provides=CreateUserUseCase)
    deactivate_user_use_case = provide(DeactivateUserHandler, provides=DeactivateUserUseCase)
    grant_admin_use_case = provide(GrantAdminHandler, provides=GrantAdminUseCase)
    revoke_admin_use_case = provide(RevokeAdminHandler, provides=RevokeAdminUseCase)
    set_user_password_use_case = provide(SetUserPasswordHandler, provides=SetUserPasswordUseCase)
    list_users_use_case = provide(ListUsersHandler, provides=ListUsersUseCase)
    current_user_use_case = provide(CurrentUserHandler, provides=CurrentUserUseCase)

    # Account Use Cases
    sign_up_use_case = provide(SignUpHandler, provides=SignUpUseCase)
    log_in_use_case = provide(LogInHandler, provides=LogInUseCase)
    log_out_use_case = provide(LogOutHandler, provides=LogOutUseCase)
    change_password_use_case = provide(ChangePasswordHandler, provides=ChangePasswordUseCase)
