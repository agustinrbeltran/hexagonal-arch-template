from fastapi import APIRouter

from account.infrastructure.http.routers.account_router import create_accounts_router
from core.infrastructure.http.routers.profile_router import create_profiles_router
from shared.infrastructure.http.controllers.health import create_health_router


def create_api_v1_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    general_router = APIRouter(tags=["General"])
    general_router.include_router(create_health_router())

    sub_routers = (
        create_accounts_router(),
        create_profiles_router(),
        general_router,
    )
    for sub_router in sub_routers:
        router.include_router(sub_router)
    return router
