from fastapi import APIRouter

from core.infrastructure.http.controllers.get_my_profile import (
    create_get_my_profile_router,
)
from core.infrastructure.http.controllers.list_profiles import (
    create_list_profiles_router,
)
from core.infrastructure.http.controllers.update_profile import (
    create_update_profile_router,
)


def create_profiles_router() -> APIRouter:
    router = APIRouter(prefix="/profiles", tags=["Profiles"])
    sub_routers = (
        create_get_my_profile_router(),
        create_update_profile_router(),
        create_list_profiles_router(),
    )
    for sub_router in sub_routers:
        router.include_router(sub_router)
    return router
