import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from account.domain.account.enums import AccountRole
from account.domain.account.events import AccountCreated
from shared.domain.domain_event import DomainEvent
from shared.infrastructure.events.registry import _event_type_registry
from shared.infrastructure.events.serialization import (
    deserialize_event,
    serialize_event,
)


@pytest.fixture(autouse=True)
def _register_event_types() -> None:
    _event_type_registry["AccountCreated"] = AccountCreated


class TestSerializeEvent:
    def test_serializes_event_to_json_string(self) -> None:
        event = AccountCreated(
            account_id=UUID("12345678-1234-5678-1234-567812345678"),
            email="test@example.com",
            role=AccountRole.USER,
        )

        result = serialize_event(event)

        parsed = json.loads(result)
        assert parsed["account_id"] == "12345678-1234-5678-1234-567812345678"
        assert parsed["email"] == "test@example.com"
        assert parsed["role"] == "user"
        assert "event_id" in parsed
        assert "occurred_at" in parsed

    def test_serializes_uuid_as_string(self) -> None:
        account_id = uuid4()
        event = AccountCreated(
            account_id=account_id,
            email="a@b.com",
            role=AccountRole.ADMIN,
        )

        result = serialize_event(event)
        parsed = json.loads(result)

        assert parsed["account_id"] == str(account_id)

    def test_serializes_datetime_as_string(self) -> None:
        now = datetime.now(UTC)
        event = AccountCreated(
            account_id=uuid4(),
            email="a@b.com",
            role=AccountRole.USER,
            occurred_at=now,
        )

        result = serialize_event(event)
        parsed = json.loads(result)

        assert isinstance(parsed["occurred_at"], str)

    def test_serializes_enum_as_value(self) -> None:
        event = AccountCreated(
            account_id=uuid4(),
            email="a@b.com",
            role=AccountRole.SUPER_ADMIN,
        )

        result = serialize_event(event)
        parsed = json.loads(result)

        assert parsed["role"] == "super_admin"


class TestDeserializeEvent:
    def test_round_trip_preserves_all_fields(self) -> None:
        original = AccountCreated(
            account_id=UUID("12345678-1234-5678-1234-567812345678"),
            email="test@example.com",
            role=AccountRole.USER,
        )

        payload = serialize_event(original)
        restored = deserialize_event("AccountCreated", payload)

        assert isinstance(restored, AccountCreated)
        assert restored.account_id == original.account_id
        assert restored.email == original.email
        assert restored.role == original.role
        assert restored.event_id == original.event_id
        assert restored.occurred_at == original.occurred_at

    def test_coerces_uuid_from_string(self) -> None:
        uid = uuid4()
        event = AccountCreated(account_id=uid, email="a@b.com", role=AccountRole.USER)
        payload = serialize_event(event)

        restored = deserialize_event("AccountCreated", payload)

        assert isinstance(restored, AccountCreated)
        assert isinstance(restored.account_id, UUID)
        assert restored.account_id == uid

    def test_coerces_datetime_from_string(self) -> None:
        now = datetime.now(UTC)
        event = AccountCreated(
            account_id=uuid4(),
            email="a@b.com",
            role=AccountRole.USER,
            occurred_at=now,
        )
        payload = serialize_event(event)

        restored = deserialize_event("AccountCreated", payload)

        assert isinstance(restored.occurred_at, datetime)

    def test_coerces_enum_from_value(self) -> None:
        event = AccountCreated(
            account_id=uuid4(),
            email="a@b.com",
            role=AccountRole.ADMIN,
        )
        payload = serialize_event(event)

        restored = deserialize_event("AccountCreated", payload)

        assert isinstance(restored, AccountCreated)
        assert isinstance(restored.role, AccountRole)
        assert restored.role == AccountRole.ADMIN

    def test_unknown_event_type_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unknown event type"):
            deserialize_event("UnknownEvent", "{}")

    def test_deserializes_base_domain_event_fields(self) -> None:
        event = AccountCreated(
            account_id=uuid4(),
            email="a@b.com",
            role=AccountRole.USER,
        )
        payload = serialize_event(event)

        restored = deserialize_event("AccountCreated", payload)

        assert isinstance(restored, DomainEvent)
        assert restored.event_type == "AccountCreated"
