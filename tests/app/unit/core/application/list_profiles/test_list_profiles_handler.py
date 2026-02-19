from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from account.domain.account.enums import AccountRole
from account.domain.account.repository import AccountRepository
from core.application.list_profiles.handler import ListProfilesHandler
from core.application.list_profiles.query import ListProfilesQuery
from core.domain.profile.repository import ListProfilesQM, ProfileRepository
from shared.domain.errors import AuthorizationError
from shared.domain.ports.identity_provider import IdentityProvider
from shared.domain.queries import SortingOrder
from tests.app.unit.factories.account_entity import create_account
from tests.app.unit.factories.value_objects import create_account_id


@pytest.mark.asyncio
async def test_admin_returns_repo_result() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)

    account_id = create_account_id()
    admin = create_account(account_id=account_id, role=AccountRole.ADMIN)
    expected: ListProfilesQM = {"profiles": [], "total": 0}
    query = ListProfilesQuery(
        limit=10, offset=0, sorting_field="username", sorting_order=SortingOrder.ASC
    )

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, account_repository.get_by_id).return_value = admin
    cast(AsyncMock, profile_repository.get_all).return_value = expected

    sut = ListProfilesHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        account_repository=cast(AccountRepository, account_repository),
        profile_repository=cast(ProfileRepository, profile_repository),
    )

    result = await sut.execute(query)

    assert result == expected


@pytest.mark.asyncio
async def test_super_admin_returns_repo_result() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)

    account_id = create_account_id()
    super_admin = create_account(account_id=account_id, role=AccountRole.SUPER_ADMIN)
    expected: ListProfilesQM = {"profiles": [], "total": 0}
    query = ListProfilesQuery(
        limit=10, offset=0, sorting_field="username", sorting_order=SortingOrder.ASC
    )

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, account_repository.get_by_id).return_value = super_admin
    cast(AsyncMock, profile_repository.get_all).return_value = expected

    sut = ListProfilesHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        account_repository=cast(AccountRepository, account_repository),
        profile_repository=cast(ProfileRepository, profile_repository),
    )

    result = await sut.execute(query)

    assert result == expected


@pytest.mark.asyncio
async def test_account_not_found_raises_authorization_error() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)

    account_id = create_account_id()
    query = ListProfilesQuery(
        limit=10, offset=0, sorting_field="username", sorting_order=SortingOrder.ASC
    )

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, account_repository.get_by_id).return_value = None

    sut = ListProfilesHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        account_repository=cast(AccountRepository, account_repository),
        profile_repository=cast(ProfileRepository, profile_repository),
    )

    with pytest.raises(AuthorizationError):
        await sut.execute(query)


@pytest.mark.asyncio
async def test_user_role_raises_authorization_error() -> None:
    identity_provider = create_autospec(IdentityProvider, instance=True)
    account_repository = create_autospec(AccountRepository, instance=True)
    profile_repository = create_autospec(ProfileRepository, instance=True)

    account_id = create_account_id()
    user = create_account(account_id=account_id, role=AccountRole.USER)
    query = ListProfilesQuery(
        limit=10, offset=0, sorting_field="username", sorting_order=SortingOrder.ASC
    )

    cast(AsyncMock, identity_provider.get_current_account_id).return_value = account_id
    cast(AsyncMock, account_repository.get_by_id).return_value = user

    sut = ListProfilesHandler(
        identity_provider=cast(IdentityProvider, identity_provider),
        account_repository=cast(AccountRepository, account_repository),
        profile_repository=cast(ProfileRepository, profile_repository),
    )

    with pytest.raises(AuthorizationError):
        await sut.execute(query)
