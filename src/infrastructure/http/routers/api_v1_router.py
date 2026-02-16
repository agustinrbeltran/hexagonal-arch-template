from fastapi import APIRouter

from infrastructure.http.controllers.health import create_health_router
from infrastructure.http.routers.account_router import create_account_router
from infrastructure.http.routers.user_router import create_users_router


def create_api_v1_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    general_router = APIRouter(tags=["General"])
    general_router.include_router(create_health_router())

    sub_routers = (
        create_account_router(),
        general_router,
        create_users_router(),
    )
    for sub_router in sub_routers:
        router.include_router(sub_router)
    return router
