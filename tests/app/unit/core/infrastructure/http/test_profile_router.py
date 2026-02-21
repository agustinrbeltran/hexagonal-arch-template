"""
Controller-level tests for the profiles router.
Expected endpoints:
  - GET  /profiles/me
  - PUT  /profiles/me
  - PATCH /profiles/me
No /me/username endpoints.
"""

from fastapi import APIRouter

from core.infrastructure.http.routers.profile_router import create_profiles_router


def _get_routes(router: APIRouter) -> list[tuple[str, str]]:
    routes: list[tuple[str, str]] = []
    for route in router.routes:
        methods = getattr(route, "methods", set()) or set()
        path = getattr(route, "path", "")
        routes.extend((method.upper(), path) for method in methods)
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
