import pytest

from domain.shared.errors import AuthorizationError
from domain.user.services import authorize
from tests.app.unit.application.authz_service.permission_stubs import (
    AlwaysAllow,
    AlwaysDeny,
    DummyContext,
)


def test_authorize_allows_when_permission_is_satisfied() -> None:
    context = DummyContext()
    permission = AlwaysAllow()

    authorize(permission, context=context)


def test_authorize_raises_when_permission_not_satisfied() -> None:
    context = DummyContext()
    permission = AlwaysDeny()

    with pytest.raises(AuthorizationError):
        authorize(permission, context=context)
