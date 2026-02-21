"""
Controller-level tests for the profiles router.
Expected endpoints:
  - GET  /profiles/me
  - PUT  /profiles/me
  - PATCH /profiles/me
No /me/username endpoints.
"""
from core.infrastructure.http.routers.profile_router import create_profiles_router


def _get_routes(router):  # type: ignore[no-untyped-def]
    routes = []
    for route in router.routes:
        methods = getattr(route, "methods", set()) or set()
        path = getattr(route, "path", "")
        for method in methods:
            routes.append((method.upper(), path))
    return routes


def test_put_me_username_does_not_exist() -> None:
    router = create_profiles_router()
    routes = _get_routes(router)
    assert ("PUT", "/profiles/me/username") not in routes


def test_patch_me_username_does_not_exist() -> None:
    router = create_profiles_router()
    routes = _get_routes(router)
    assert ("PATCH", "/profiles/me/username") not in routes


def test_put_me_exists() -> None:
    router = create_profiles_router()
    routes = _get_routes(router)
    assert ("PUT", "/profiles/me") in routes


def test_patch_me_exists() -> None:
    router = create_profiles_router()
    routes = _get_routes(router)
    assert ("PATCH", "/profiles/me") in routes
