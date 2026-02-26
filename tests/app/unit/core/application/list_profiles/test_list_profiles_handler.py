from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from core.application.list_profiles.handler import ListProfilesHandler
from core.application.list_profiles.query import ListProfilesQuery
from core.domain.profile.repository import ListProfilesQM, ProfileRepository
from shared.domain.errors import AuthorizationError
from shared.domain.ports.authorization_guard import AuthorizationGuard
from shared.domain.queries import SortingOrder


@pytest.mark.asyncio
async def test_admin_returns_repo_result() -> None:
    authorization_guard = create_autospec(AuthorizationGuard, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)

    expected: ListProfilesQM = {"profiles": [], "total": 0}
    query = ListProfilesQuery(
        limit=10, offset=0, sorting_field="username", sorting_order=SortingOrder.ASC
    )

    cast(AsyncMock, profile_repository.get_all).return_value = expected

    sut = ListProfilesHandler(
        authorization_guard=cast(AuthorizationGuard, authorization_guard),
        profile_repository=cast(ProfileRepository, profile_repository),
    )

    result = await sut.execute(query)

    assert result == expected
    cast(AsyncMock, authorization_guard.require_admin).assert_awaited_once()


@pytest.mark.asyncio
async def test_non_admin_raises_authorization_error() -> None:
    authorization_guard = create_autospec(AuthorizationGuard, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)

    query = ListProfilesQuery(
        limit=10, offset=0, sorting_field="username", sorting_order=SortingOrder.ASC
    )

    cast(AsyncMock, authorization_guard.require_admin).side_effect = AuthorizationError(
        "Insufficient permissions."
    )

    sut = ListProfilesHandler(
        authorization_guard=cast(AuthorizationGuard, authorization_guard),
        profile_repository=cast(ProfileRepository, profile_repository),
    )

    with pytest.raises(AuthorizationError):
        await sut.execute(query)

    cast(AsyncMock, profile_repository.get_all).assert_not_awaited()
