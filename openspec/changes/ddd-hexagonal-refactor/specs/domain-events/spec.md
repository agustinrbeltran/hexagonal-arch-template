## ADDED Requirements

### Requirement: Aggregates collect domain events internally
Every aggregate root MUST maintain an internal `_events: list[DomainEvent]` field. Business methods on the aggregate MUST register relevant events via `_register_event(event)`. Events are NOT dispatched immediately — they accumulate until collected.

#### Scenario: Business method registers an event
- **WHEN** a User aggregate's creation factory method is called
- **THEN** a `UserCreated` event is added to the aggregate's `_events` list

#### Scenario: Events accumulate across multiple operations
- **WHEN** multiple business methods are called on the same aggregate instance
- **THEN** all events are present in the `_events` list in order

### Requirement: collect_events() returns and clears events
The `AggregateRoot.collect_events()` method MUST return all accumulated events as a list and clear the internal `_events` list. This MUST be called by the application layer after persisting the aggregate.

#### Scenario: collect_events returns accumulated events
- **WHEN** `collect_events()` is called on an aggregate with 3 pending events
- **THEN** a list of 3 `DomainEvent` instances is returned

#### Scenario: collect_events clears the list
- **WHEN** `collect_events()` is called
- **THEN** a subsequent call to `collect_events()` returns an empty list

### Requirement: In-process event dispatcher
The system SHALL provide an `EventDispatcher` in `application/shared/event_dispatcher.py` that accepts a list of `DomainEvent` instances and invokes registered handlers. The dispatcher is a driven port — the in-process implementation lives in infrastructure.

#### Scenario: Dispatcher invokes registered handlers
- **WHEN** a `UserCreated` event is dispatched
- **THEN** all handlers registered for `UserCreated` are invoked with the event

#### Scenario: Unhandled events are silently ignored
- **WHEN** a domain event is dispatched and no handlers are registered for its type
- **THEN** no error is raised — the event is simply not processed

### Requirement: Use case handlers dispatch events after commit
Application-layer handlers MUST collect events from aggregates after persisting changes and dispatch them via the `EventDispatcher` port. Events MUST be dispatched after the unit of work commits successfully.

#### Scenario: Events dispatched after successful commit
- **WHEN** a use case handler commits changes via unit of work
- **THEN** `collect_events()` is called on the aggregate and events are dispatched

#### Scenario: Events are NOT dispatched on rollback
- **WHEN** a use case handler encounters an error and rolls back
- **THEN** no domain events are dispatched
