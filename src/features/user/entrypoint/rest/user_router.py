from fastapi import APIRouter

from features.user.entrypoint.rest.controllers.activate_user import (
    create_activate_user_router,
)
from features.user.entrypoint.rest.controllers.create_user import (
    create_create_user_router,
)
from features.user.entrypoint.rest.controllers.deactivate_user import (
    create_deactivate_user_router,
)
from features.user.entrypoint.rest.controllers.grant_admin import (
    create_grant_admin_router,
)
from features.user.entrypoint.rest.controllers.list_users import create_list_users_router
from features.user.entrypoint.rest.controllers.revoke_admin import (
    create_revoke_admin_router,
)
from features.user.entrypoint.rest.controllers.set_user_password import (
    create_set_user_password_router,
)


def create_users_router() -> APIRouter:
    router = APIRouter(
        prefix="/users",
        tags=["Users"],
    )

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
