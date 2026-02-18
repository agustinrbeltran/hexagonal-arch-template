## MODIFIED Requirements

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
The system SHALL provide a `@handles(EventType)` class decorator in `shared/infrastructure/events/registry.py` that registers the decorated class in a module-level registry mapping `type[DomainEvent] → list[type[EventHandler]]`. A class MAY be decorated with multiple `@handles(...)` for different event types.

#### Scenario: Single event type registration
- **GIVEN** a handler class decorated with `@handles(AccountCreated)`
- **WHEN** the module is imported
- **THEN** the class is registered as a handler for `AccountCreated`

#### Scenario: Multiple event type registration
- **GIVEN** a handler class decorated with `@handles(AccountCreated)` and `@handles(AccountActivated)`
- **WHEN** the module is imported
- **THEN** the class is registered as a handler for both event types

### Requirement: Dispatcher resolves handlers from DI container
The `InProcessEventDispatcher` SHALL receive a Dishka `AsyncContainer` and for each dispatched event: look up handler classes from the registry, resolve each from the container, and call `handle(event)`.

#### Scenario: Handler with dependencies is resolved
- **GIVEN** a handler that depends on `ProfileRepository` in its constructor
- **WHEN** the dispatcher resolves the handler from the container
- **THEN** the handler receives the repository instance via DI

#### Scenario: No handlers registered for event type
- **WHEN** an event is dispatched and no handlers are registered for its type
- **THEN** the event is silently ignored (no error raised)

### Requirement: Concurrent dispatch with error isolation
The dispatcher SHALL invoke all handlers for a given event concurrently using `asyncio.gather(*tasks, return_exceptions=True)`. If any handler raises an exception, it MUST be logged and swallowed — it MUST NOT prevent other handlers from executing.

#### Scenario: Concurrent execution
- **GIVEN** two handlers registered for `AccountCreated`
- **WHEN** an `AccountCreated` event is dispatched
- **THEN** both handlers are invoked concurrently via `asyncio.gather`

#### Scenario: Error isolation
- **GIVEN** two handlers registered for `AccountCreated`, one of which raises an exception
- **WHEN** an `AccountCreated` event is dispatched
- **THEN** the failing handler's error is logged
- **AND** the other handler completes successfully

### Requirement: Handler classes registered in Dishka
Each concrete event handler class SHALL be registered in Dishka providers within their respective bounded contexts. Account BC handlers in Account's DI provider, Core BC handlers in Core's DI provider. All with `Scope.REQUEST`.

#### Scenario: Cross-context handler DI registration
- **GIVEN** `CreateProfileOnAccountCreated` is registered in Core BC's DI provider
- **WHEN** the container resolves `CreateProfileOnAccountCreated`
- **THEN** the instance is created with Core BC dependencies (ProfileRepository, CoreUnitOfWork, etc.)

## ADDED Requirements

### Requirement: CreateProfileOnAccountCreated event handler
The system SHALL provide a `CreateProfileOnAccountCreated` handler in `core/infrastructure/events/handlers/` decorated with `@handles(AccountCreated)`. It SHALL create an empty Profile (username=None) for the account referenced in the event, using `ProfileIdGenerator`, `ProfileRepository`, and `CoreUnitOfWork`.

#### Scenario: Profile created on account creation
- **WHEN** an `AccountCreated` event is dispatched
- **THEN** `CreateProfileOnAccountCreated` creates a Profile with `account_id=event.account_id` and `username=None`

#### Scenario: Profile creation commits independently
- **WHEN** `CreateProfileOnAccountCreated` handles the event
- **THEN** it commits via `CoreUnitOfWork` in a separate transaction from the Account creation
