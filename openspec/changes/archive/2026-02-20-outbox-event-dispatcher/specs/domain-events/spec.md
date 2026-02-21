## MODIFIED Requirements

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
