from fastapi import APIRouter

from infrastructure.http.controllers.user.activate_user import (
    create_activate_user_router,
)
from infrastructure.http.controllers.user.create_user import create_create_user_router
from infrastructure.http.controllers.user.deactivate_user import (
    create_deactivate_user_router,
)
from infrastructure.http.controllers.user.grant_admin import create_grant_admin_router
from infrastructure.http.controllers.user.list_users import create_list_users_router
from infrastructure.http.controllers.user.revoke_admin import create_revoke_admin_router
from infrastructure.http.controllers.user.set_user_password import (
    create_set_user_password_router,
)


def create_users_router() -> APIRouter:
    router = APIRouter(prefix="/users", tags=["Users"])
    sub_routers = (
        create_create_user_router(),
        create_list_users_router(),
        create_set_user_password_router(),
        create_grant_admin_router(),
        create_revoke_admin_router(),
        create_activate_user_router(),
        create_deactivate_user_router(),
    )
    for sub_router in sub_routers:
        router.include_router(sub_router)
    return router
