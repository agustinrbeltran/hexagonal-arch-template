from fastapi import APIRouter

from account.infrastructure.http.controllers.activate_account import (
    create_activate_account_router,
)
from account.infrastructure.http.controllers.change_password import (
    create_change_password_router,
)
from account.infrastructure.http.controllers.create_account import (
    create_create_account_router,
)
from account.infrastructure.http.controllers.current_account import (
    create_current_account_router,
)
from account.infrastructure.http.controllers.deactivate_account import (
    create_deactivate_account_router,
)
from account.infrastructure.http.controllers.grant_admin import (
    create_grant_admin_router,
)
from account.infrastructure.http.controllers.list_accounts import (
    create_list_accounts_router,
)
from account.infrastructure.http.controllers.log_in import create_log_in_router
from account.infrastructure.http.controllers.refresh import create_refresh_router
from account.infrastructure.http.controllers.revoke_admin import (
    create_revoke_admin_router,
)
from account.infrastructure.http.controllers.set_account_password import (
    create_set_account_password_router,
)
from account.infrastructure.http.controllers.sign_up import create_sign_up_router


def create_accounts_router() -> APIRouter:
    router = APIRouter(prefix="/accounts", tags=["Accounts"])
    sub_routers = (
        create_sign_up_router(),
        create_log_in_router(),
        create_change_password_router(),
        create_refresh_router(),
        create_current_account_router(),
        create_create_account_router(),
        create_list_accounts_router(),
        create_set_account_password_router(),
        create_grant_admin_router(),
        create_revoke_admin_router(),
        create_activate_account_router(),
        create_deactivate_account_router(),
    )
    for sub_router in sub_routers:
        router.include_router(sub_router)
    return router
