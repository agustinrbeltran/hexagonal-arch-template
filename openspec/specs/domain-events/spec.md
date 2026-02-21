### Requirement: Aggregates collect domain events internally
Every aggregate root MUST maintain an internal `_events: list[DomainEvent]` field. Business methods on the aggregate MUST register relevant events via `_register_event(event)`. Events are NOT dispatched immediately — they accumulate until collected. This applies to both `Account` (Account BC) and `Profile` (Core BC) aggregates.

#### Scenario: Business method registers an event
- **WHEN** an Account aggregate's creation factory method is called
- **THEN** an `AccountCreated` event is added to the aggregate's `_events` list

#### Scenario: Profile business method registers an event
- **WHEN** a Profile aggregate's `set_username()` method is called with a new username
- **THEN** a `UsernameChanged` event is added to the aggregate's `_events` list

#### Scenario: Events accumulate across multiple operations
- **WHEN** multiple business methods are called on the same aggregate instance
- **THEN** all events are present in the `_events` list in order

### Requirement: In-process event dispatcher
The system SHALL provide an `EventDispatcher` protocol in `shared/application/event_dispatcher.py` (shared kernel) that accepts a list of `DomainEvent` instances. The protocol defines a single async method `dispatch(events: list[DomainEvent]) -> None`. The concrete implementation is the `OutboxEventDispatcher` which writes events to an outbox table within the same database session, rather than invoking handlers directly.

#### Scenario: Dispatcher writes events to outbox
- **WHEN** an `AccountCreated` event is dispatched
- **THEN** an outbox entry is created in the session with the serialized event

#### Scenario: Unhandled events are still persisted
- **WHEN** a domain event is dispatched and no handlers are registered for its type
- **THEN** the event is still written to the outbox (handlers are resolved later by the relay)

### Requirement: Use case handlers dispatch events before commit
Application-layer handlers MUST collect events from aggregates and dispatch them via the `EventDispatcher` port BEFORE the unit of work commits. This ensures outbox entries are part of the same database transaction as the aggregate state change. Events and aggregate state are committed atomically.

#### Scenario: Events dispatched before commit
- **WHEN** a use case handler persists an aggregate and dispatches events
- **THEN** `event_dispatcher.dispatch(events)` is called before `unit_of_work.commit()`

#### Scenario: Atomic commit of aggregate and events
- **WHEN** `SignUpHandler` dispatches `AccountCreated` and commits via `AccountUnitOfWork`
- **THEN** the account row and the outbox row are committed in a single transaction

#### Scenario: Events are NOT persisted on rollback
- **WHEN** a use case handler encounters an error and the transaction rolls back
- **THEN** both the aggregate state and outbox entries are rolled back
