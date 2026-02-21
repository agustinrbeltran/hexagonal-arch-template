from unittest.mock import MagicMock, create_autospec
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from account.domain.account.enums import AccountRole
from account.domain.account.events import AccountActivated, AccountCreated
from shared.infrastructure.events.dispatcher import OutboxEventDispatcher
from shared.infrastructure.persistence.mappers.outbox import OutboxRecord


@pytest.fixture
def mock_session() -> MagicMock:
    return create_autospec(AsyncSession, instance=True)  # type: ignore[no-any-return]


@pytest.fixture
def dispatcher(mock_session: MagicMock) -> OutboxEventDispatcher:
    return OutboxEventDispatcher(session=mock_session)


class TestOutboxEventDispatcher:
    @pytest.mark.asyncio
    async def test_single_event_adds_one_record(
        self, dispatcher: OutboxEventDispatcher, mock_session: MagicMock
    ) -> None:
        event = AccountCreated(
            account_id=uuid4(), email="a@b.com", role=AccountRole.USER
        )

        await dispatcher.dispatch([event])

        mock_session.add.assert_called_once()
        record = mock_session.add.call_args[0][0]
        assert isinstance(record, OutboxRecord)
        assert record.event_type == "AccountCreated"
        assert record.delivered is False
        assert record.retry_count == 0

    @pytest.mark.asyncio
    async def test_multiple_events_add_multiple_records(
        self, dispatcher: OutboxEventDispatcher, mock_session: MagicMock
    ) -> None:
        events = [
            AccountCreated(account_id=uuid4(), email="a@b.com", role=AccountRole.USER),
            AccountActivated(account_id=uuid4()),
        ]

        await dispatcher.dispatch(events)

        assert mock_session.add.call_count == 2

    @pytest.mark.asyncio
    async def test_does_not_flush_or_commit(
        self, dispatcher: OutboxEventDispatcher, mock_session: MagicMock
    ) -> None:
        event = AccountCreated(
            account_id=uuid4(), email="a@b.com", role=AccountRole.USER
        )

        await dispatcher.dispatch([event])

        mock_session.flush.assert_not_called()
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_events_list(
        self, dispatcher: OutboxEventDispatcher, mock_session: MagicMock
    ) -> None:
        await dispatcher.dispatch([])

        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_record_event_type_matches_class_name(
        self, dispatcher: OutboxEventDispatcher, mock_session: MagicMock
    ) -> None:
        event = AccountActivated(account_id=uuid4())

        await dispatcher.dispatch([event])

        record = mock_session.add.call_args[0][0]
        assert record.event_type == "AccountActivated"

    @pytest.mark.asyncio
    async def test_record_payload_is_json_string(
        self, dispatcher: OutboxEventDispatcher, mock_session: MagicMock
    ) -> None:
        event = AccountCreated(
            account_id=uuid4(), email="a@b.com", role=AccountRole.USER
        )

        await dispatcher.dispatch([event])

        record = mock_session.add.call_args[0][0]
        assert isinstance(record.payload, str)
        assert "a@b.com" in record.payload

    @pytest.mark.asyncio
    async def test_record_occurred_at_from_event(
        self, dispatcher: OutboxEventDispatcher, mock_session: MagicMock
    ) -> None:
        event = AccountCreated(
            account_id=uuid4(), email="a@b.com", role=AccountRole.USER
        )

        await dispatcher.dispatch([event])

        record = mock_session.add.call_args[0][0]
        assert record.occurred_at == event.occurred_at
