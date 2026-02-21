from typing import cast
from unittest.mock import MagicMock, create_autospec

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.infrastructure.persistence.sqla_profile_repository import (
    SqlaProfileRepository,
)
from shared.infrastructure.persistence.types_ import MainAsyncSession
from tests.app.unit.factories.profile_entity import create_profile


def _make_session() -> tuple[MagicMock, MagicMock]:
    """Return (async_session_mock, sync_session_mock)."""
    sync_session = create_autospec(Session, instance=True)
    session = create_autospec(AsyncSession, instance=True)
    session.sync_session = sync_session
    return session, sync_session


class TestSqlaProfileRepositorySave:
    def test_save_new_profile_calls_merge(self) -> None:
        session, sync_session = _make_session()
        repo = SqlaProfileRepository(session=cast(MainAsyncSession, session))
        profile = create_profile()

        repo.save(profile)

        sync_session.merge.assert_called_once()

    def test_save_existing_profile_calls_merge(self) -> None:
        session, sync_session = _make_session()
        repo = SqlaProfileRepository(session=cast(MainAsyncSession, session))
        profile = create_profile()

        repo.save(profile)
        repo.save(profile)

        assert sync_session.merge.call_count == 2

    def test_save_does_not_call_add(self) -> None:
        session, sync_session = _make_session()
        repo = SqlaProfileRepository(session=cast(MainAsyncSession, session))
        profile = create_profile()

        repo.save(profile)

        sync_session.add.assert_not_called()

    def test_save_passes_converted_record_to_merge(self) -> None:
        session, sync_session = _make_session()
        repo = SqlaProfileRepository(session=cast(MainAsyncSession, session))
        profile = create_profile()

        repo.save(profile)

        record = sync_session.merge.call_args[0][0]
        assert record.id == profile.id_.value
        assert record.account_id == profile.account_id.value
