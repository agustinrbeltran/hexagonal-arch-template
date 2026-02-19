## MODIFIED Requirements

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
The system SHALL provide an `EventDispatcher` in `shared/application/event_dispatcher.py` (shared kernel) that accepts a list of `DomainEvent` instances and invokes registered handlers. The dispatcher is a driven port — the in-process implementation lives in shared infrastructure.

#### Scenario: Dispatcher invokes registered handlers
- **WHEN** an `AccountCreated` event is dispatched
- **THEN** all handlers registered for `AccountCreated` are invoked with the event, including cross-context handlers

#### Scenario: Unhandled events are silently ignored
- **WHEN** a domain event is dispatched and no handlers are registered for its type
- **THEN** no error is raised — the event is simply not processed

### Requirement: Use case handlers dispatch events after commit
Application-layer handlers MUST collect events from aggregates after persisting changes and dispatch them via the `EventDispatcher` port. Events MUST be dispatched after the unit of work commits successfully. This applies to handlers in both Account and Core bounded contexts.

#### Scenario: Events dispatched after successful commit
- **WHEN** a use case handler commits changes via its context's unit of work
- **THEN** `collect_events()` is called on the aggregate and events are dispatched

#### Scenario: Cross-context event dispatched
- **WHEN** `SignUpHandler` commits an Account and dispatches `AccountCreated`
- **THEN** the `CreateProfileOnAccountCreated` handler in Core BC is invoked

#### Scenario: Events are NOT dispatched on rollback
- **WHEN** a use case handler encounters an error and rolls back
- **THEN** no domain events are dispatched
