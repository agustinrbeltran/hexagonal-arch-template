from typing import cast
from unittest.mock import AsyncMock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.infrastructure.persistence.sqla_profile_repository import (
    SqlaProfileRepository,
)
from shared.infrastructure.persistence.types_ import MainAsyncSession
from tests.app.unit.factories.profile_entity import create_profile


def _make_session() -> AsyncMock:
    session = create_autospec(AsyncSession, instance=True)
    return session


class TestSqlaProfileRepositorySave:
    @pytest.mark.asyncio
    async def test_save_calls_merge(self) -> None:
        session = _make_session()
        repo = SqlaProfileRepository(session=cast(MainAsyncSession, session))
        profile = create_profile()

        await repo.save(profile)

        session.merge.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_save_passes_converted_record_to_merge(self) -> None:
        session = _make_session()
        repo = SqlaProfileRepository(session=cast(MainAsyncSession, session))
        profile = create_profile()

        await repo.save(profile)

        record = session.merge.call_args[0][0]
        assert record.id == profile.id_.value
        assert record.account_id == profile.account_id.value

    @pytest.mark.asyncio
    async def test_save_twice_calls_merge_twice(self) -> None:
        session = _make_session()
        repo = SqlaProfileRepository(session=cast(MainAsyncSession, session))
        profile = create_profile()

        await repo.save(profile)
        await repo.save(profile)

        assert session.merge.await_count == 2
