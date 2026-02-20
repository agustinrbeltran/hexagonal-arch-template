import dataclasses
import json
import types
import typing
from datetime import datetime
from enum import Enum
from typing import get_type_hints
from uuid import UUID

from shared.domain.domain_event import DomainEvent
from shared.infrastructure.events.registry import get_event_class

_UNION_ORIGINS = {typing.Union, types.UnionType}


def serialize_event(event: DomainEvent) -> str:
    return json.dumps(dataclasses.asdict(event), default=str)


def deserialize_event(event_type: str, payload: str) -> DomainEvent:
    event_cls = get_event_class(event_type)
    if event_cls is None:
        msg = f"Unknown event type: {event_type}"
        raise ValueError(msg)

    raw = json.loads(payload)
    hints = get_type_hints(event_cls)

    coerced: dict[str, object] = {}
    for field_name, value in raw.items():
        expected = hints.get(field_name)
        coerced[field_name] = _coerce(value, expected)

    return event_cls(**coerced)


def _coerce(value: object, expected: type | None) -> object:
    if value is None or expected is None:
        return value

    origin = getattr(expected, "__origin__", None)

    if origin in _UNION_ORIGINS:
        args = expected.__args__  # type: ignore[union-attr]
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            return _coerce(value, non_none[0])

    if expected is UUID:
        return UUID(str(value))

    if expected is datetime:
        return datetime.fromisoformat(value) if isinstance(value, str) else value

    if isinstance(expected, type) and issubclass(expected, Enum):
        return expected(value)

    return value
