### Requirement: EventHandler protocol as application port
The system SHALL define an `EventHandler[E]` protocol in `shared/application/event_handler.py` (shared kernel). It MUST be generic over a `DomainEvent` subtype `E` and declare a single async method `handle(self, event: E) -> None`.

#### Scenario: Handler protocol contract
- **GIVEN** a class implementing `EventHandler[AccountCreated]`
- **WHEN** `handle(event)` is called with an `AccountCreated` instance
- **THEN** the handler processes the event asynchronously

### Requirement: Auto-discovery of handler modules
The system SHALL provide an `auto_discover_handlers()` function in `shared/infrastructure/events/registry.py` that scans handler packages from **all bounded contexts**: `account.infrastructure.events.handlers` and `core.infrastructure.events.handlers`. It SHALL use `pkgutil.walk_packages` to import all modules, triggering `@handles()` decorators to populate the registry. This function MUST be called at application startup.

#### Scenario: Account context handler auto-discovered
- **GIVEN** a Python module in `account/infrastructure/events/handlers/` containing a `@handles`-decorated class
- **WHEN** `auto_discover_handlers()` runs at startup
- **THEN** the handler is registered without any manual import or wiring

#### Scenario: Core context handler auto-discovered
- **GIVEN** a Python module in `core/infrastructure/events/handlers/` containing a `@handles`-decorated class
- **WHEN** `auto_discover_handlers()` runs at startup
- **THEN** the handler is registered without any manual import or wiring

#### Scenario: Cross-context handler discovered
- **GIVEN** `CreateProfileOnAccountCreated` handler in `core/infrastructure/events/handlers/`
- **WHEN** `auto_discover_handlers()` runs
- **THEN** the handler is registered for `AccountCreated` events defined in Account BC

### Requirement: @handles decorator registers handler classes
The system SHALL provide a `@handles(EventType)` class decorator in `shared/infrastructure/events/registry.py` that registers the decorated class in a module-level registry mapping `type[DomainEvent] -> list[type[EventHandler]]`. A class MAY be decorated with multiple `@handles(...)` for different event types. Additionally, the decorator SHALL register each event type in an event type name registry mapping `str -> type[DomainEvent]` (e.g., `"AccountCreated" -> AccountCreated`), enabling deserialization of outbox payloads.

#### Scenario: Single event type registration
- **GIVEN** a handler class decorated with `@handles(AccountCreated)`
- **WHEN** the module is imported
- **THEN** the class is registered as a handler for `AccountCreated`
- **AND** `"AccountCreated"` is mapped to the `AccountCreated` class in the event type registry

#### Scenario: Multiple event type registration
- **GIVEN** a handler class decorated with `@handles(AccountCreated)` and `@handles(AccountActivated)`
- **WHEN** the module is imported
- **THEN** the class is registered as a handler for both event types
- **AND** both event type names are mapped to their respective classes

#### Scenario: Event type registry lookup
- **WHEN** `get_event_class("AccountCreated")` is called
- **THEN** the `AccountCreated` class is returned

#### Scenario: Unknown event type lookup
- **WHEN** `get_event_class("UnknownEvent")` is called
- **THEN** `None` is returned

### Requirement: Dispatcher resolves handlers from DI container
The `OutboxRelay` SHALL receive a Dishka `AsyncContainer` (app-level) and for each outbox entry: deserialize the event, look up handler classes from the handler registry, create a child `Scope.REQUEST` scope, resolve each handler from the child scope, call `handle(event)`, and close the child scope.

#### Scenario: Handler with dependencies is resolved
- **GIVEN** a handler that depends on `ProfileRepository` in its constructor
- **WHEN** the relay resolves the handler from a child scope
- **THEN** the handler receives the repository instance via DI

#### Scenario: No handlers registered for event type
- **WHEN** the relay processes an outbox entry whose event type has no registered handlers
- **THEN** the entry is marked as delivered (no handlers to run)

### Requirement: Concurrent dispatch with error isolation
The relay SHALL invoke all handlers for a given event sequentially (one handler per child scope). If any handler raises an exception, it MUST be logged — it MUST NOT prevent other handlers for the same event from executing. Failed entries SHALL have their `retry_count` incremented.

#### Scenario: Error isolation between handlers
- **GIVEN** two handlers registered for `AccountCreated`, one of which raises an exception
- **WHEN** the relay processes the outbox entry
- **THEN** the failing handler's error is logged
- **AND** the other handler completes successfully

### Requirement: Handler classes registered in Dishka
Each concrete event handler class SHALL be registered in Dishka providers within their respective bounded contexts. Account BC handlers in Account's DI provider, Core BC handlers in Core's DI provider. All with `Scope.REQUEST`. The relay creates child scopes from the app container, which has access to all providers.

#### Scenario: Cross-context handler DI registration
- **GIVEN** `CreateProfileOnAccountCreated` is registered in the event handler DI provider
- **WHEN** the relay creates a child scope and resolves `CreateProfileOnAccountCreated`
- **THEN** the instance is created with Core BC dependencies (ProfileRepository, CoreUnitOfWork, etc.)

### Requirement: CreateProfileOnAccountCreated event handler
The system SHALL provide a `CreateProfileOnAccountCreated` handler in `core/infrastructure/events/handlers/` decorated with `@handles(AccountCreated)`. It SHALL create an empty Profile (username=None) for the account referenced in the event, using `ProfileIdGenerator`, `ProfileRepository`, and `CoreUnitOfWork`.

#### Scenario: Profile created on account creation
- **WHEN** an `AccountCreated` event is dispatched
- **THEN** `CreateProfileOnAccountCreated` creates a Profile with `account_id=event.account_id` and `username=None`

#### Scenario: Profile creation commits independently
- **WHEN** `CreateProfileOnAccountCreated` handles the event
- **THEN** it commits via `CoreUnitOfWork` in a separate transaction from the Account creation
