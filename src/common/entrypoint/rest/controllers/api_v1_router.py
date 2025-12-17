from fastapi import APIRouter

from common.entrypoint.rest.controllers.router import create_general_router
from features.account.entrypoint.rest.account_router import create_account_router
from features.user.entrypoint.rest.user_router import create_users_router


def create_api_v1_router() -> APIRouter:
    router = APIRouter(
        prefix="/api/v1",
    )

    sub_routers = (
        create_account_router(),
        create_general_router(),
        create_users_router(),
    )

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router
