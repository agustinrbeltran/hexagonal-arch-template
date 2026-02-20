## ADDED Requirements

### Requirement: Outbox table for event persistence
The system SHALL provide an `outbox` PostgreSQL table with columns: `id` (UUID PK), `event_type` (TEXT NOT NULL), `payload` (JSONB NOT NULL), `occurred_at` (TIMESTAMPTZ NOT NULL), `delivered` (BOOLEAN NOT NULL DEFAULT false), `delivered_at` (TIMESTAMPTZ NULL), `retry_count` (INT NOT NULL DEFAULT 0). A partial index SHALL exist on `occurred_at` WHERE `delivered = false`.

#### Scenario: Outbox entry created during transaction
- **WHEN** the `OutboxEventDispatcher` dispatches an `AccountCreated` event
- **THEN** an `outbox` row is added to the session with `event_type="AccountCreated"`, serialized payload, `delivered=false`, and `retry_count=0`

#### Scenario: Outbox entry committed atomically with aggregate
- **WHEN** the use case handler commits via `AccountUnitOfWork`
- **THEN** the outbox row and the account row are committed in the same database transaction

### Requirement: OutboxRecord persistence record
The system SHALL provide an `OutboxRecord` dataclass in `shared/infrastructure/persistence/mappers/outbox.py` mapped imperatively to the `outbox` table via `mapper_registry`. The mapper function SHALL be called during app startup alongside other table mappers.

#### Scenario: OutboxRecord mapped to outbox table
- **GIVEN** the app has started and `map_outbox_table()` has been called
- **WHEN** an `OutboxRecord` instance is added to a SQLAlchemy session
- **THEN** it is persisted to the `outbox` table

### Requirement: OutboxEventDispatcher writes events to session
The system SHALL provide an `OutboxEventDispatcher` class in `shared/infrastructure/events/dispatcher.py` implementing the `EventDispatcher` protocol. It SHALL accept a `MainAsyncSession` and for each event: create an `OutboxRecord` with the serialized event and add it to the session. It SHALL NOT flush or commit.

#### Scenario: Single event dispatched
- **WHEN** `dispatch([account_created_event])` is called
- **THEN** one `OutboxRecord` is added to the session with `event_type="AccountCreated"` and the JSON-serialized payload

#### Scenario: Multiple events dispatched
- **WHEN** `dispatch([event_a, event_b])` is called
- **THEN** two `OutboxRecord` instances are added to the session

#### Scenario: Dispatcher does not commit
- **WHEN** `dispatch(events)` is called
- **THEN** no `flush()` or `commit()` is called on the session

### Requirement: Event serialization
The system SHALL provide a `serialize_event(event: DomainEvent) -> str` function in `shared/infrastructure/events/serialization.py` that converts a domain event to a JSON string using `json.dumps(dataclasses.asdict(event), default=str)`.

#### Scenario: Event with UUID and datetime fields serialized
- **WHEN** an `AccountCreated` event with `account_id=UUID(...)`, `email="a@b.com"`, `role=AccountRole.USER` is serialized
- **THEN** the result is a JSON string with all fields as strings

### Requirement: Event deserialization
The system SHALL provide a `deserialize_event(event_type: str, payload: str) -> DomainEvent` function in `shared/infrastructure/events/serialization.py`. It SHALL look up the event class from the event type registry, parse the JSON payload, coerce fields to their annotated types (UUID, datetime, enums), and return a reconstructed domain event instance.

#### Scenario: Deserialized event matches original
- **GIVEN** an `AccountCreated` event was serialized to JSON
- **WHEN** `deserialize_event("AccountCreated", payload)` is called
- **THEN** the returned event has the same `account_id`, `email`, `role`, `event_id`, and `occurred_at` as the original

#### Scenario: Unknown event type raises error
- **WHEN** `deserialize_event("UnknownEvent", payload)` is called
- **THEN** a `ValueError` is raised

### Requirement: Polling outbox relay
The system SHALL provide an `OutboxRelay` class in `shared/infrastructure/events/relay.py` that runs as a long-lived coroutine. It SHALL poll the `outbox` table every 30 seconds for entries WHERE `delivered = false` AND `retry_count < max_retries`, ordered by `occurred_at`. For each entry, it SHALL deserialize the event, resolve handlers from the registry, execute each handler in an isolated Dishka child scope, and mark the entry as `delivered = true` with `delivered_at` set.

#### Scenario: Undelivered event processed
- **GIVEN** an outbox entry with `delivered=false` and `retry_count=0`
- **WHEN** the relay polls
- **THEN** the event is deserialized, handlers are executed, and the entry is marked `delivered=true`

#### Scenario: No undelivered events
- **WHEN** the relay polls and finds no undelivered entries
- **THEN** it sleeps for 30 seconds and polls again

#### Scenario: Handler executed in isolated Dishka scope
- **WHEN** the relay processes an outbox entry
- **THEN** each handler is resolved from a new `Scope.REQUEST` child scope with its own `MainAsyncSession` and UoW

### Requirement: Relay retry with max attempts
When a handler raises an exception during relay processing, the relay SHALL increment the outbox entry's `retry_count`, log the error, and leave `delivered = false`. On subsequent polls, entries with `retry_count >= max_retries` SHALL be skipped. A critical-level log SHALL be emitted when an entry reaches max retries.

#### Scenario: Handler failure increments retry count
- **GIVEN** an outbox entry with `retry_count=0`
- **WHEN** a handler raises an exception during processing
- **THEN** `retry_count` is updated to `1` and `delivered` remains `false`

#### Scenario: Max retries reached
- **GIVEN** an outbox entry with `retry_count = max_retries`
- **WHEN** the relay polls
- **THEN** the entry is skipped and a critical-level log is emitted

### Requirement: Relay graceful shutdown
The relay SHALL catch `asyncio.CancelledError` and exit its poll loop cleanly. The FastAPI lifespan SHALL cancel the relay task before closing the Dishka container.

#### Scenario: Server shutdown during sleep
- **WHEN** the relay is sleeping between polls and the server shuts down
- **THEN** the relay task is cancelled and exits without error

#### Scenario: Server shutdown during processing
- **WHEN** the relay is processing an outbox entry and the server shuts down
- **THEN** the relay catches `CancelledError` and exits, leaving in-progress entries as undelivered for the next startup

### Requirement: DI wiring for OutboxEventDispatcher
The `OutboxEventDispatcher` SHALL be registered in Dishka at `Scope.REQUEST`, receiving `MainAsyncSession`. It SHALL replace the current `InProcessEventDispatcher` in the provider that satisfies the `EventDispatcher` protocol.

#### Scenario: Dispatcher injected into use case handler
- **GIVEN** `SignUpHandler` depends on `EventDispatcher`
- **WHEN** Dishka resolves `EventDispatcher` for a request
- **THEN** an `OutboxEventDispatcher` instance with the request's `MainAsyncSession` is provided
