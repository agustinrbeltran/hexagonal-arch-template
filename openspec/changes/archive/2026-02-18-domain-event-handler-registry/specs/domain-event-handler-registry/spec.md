## ADDED Requirements

### Requirement: EventHandler protocol as application port
The system SHALL define an `EventHandler[E]` protocol in `application/shared/event_handler.py`. It MUST be generic over a `DomainEvent` subtype `E` and declare a single async method `handle(self, event: E) -> None`.

#### Scenario: Handler protocol contract
- **GIVEN** a class implementing `EventHandler[UserCreated]`
- **WHEN** `handle(event)` is called with a `UserCreated` instance
- **THEN** the handler processes the event asynchronously

### Requirement: @handles decorator registers handler classes
The system SHALL provide a `@handles(EventType)` class decorator in `infrastructure/events/registry.py` that registers the decorated class in a module-level registry mapping `type[DomainEvent] → list[type[EventHandler]]`. A class MAY be decorated with multiple `@handles(...)` for different event types.

#### Scenario: Single event type registration
- **GIVEN** a handler class decorated with `@handles(UserCreated)`
- **WHEN** the module is imported
- **THEN** the class is registered as a handler for `UserCreated`

#### Scenario: Multiple event type registration
- **GIVEN** a handler class decorated with `@handles(UserCreated)` and `@handles(UserActivated)`
- **WHEN** the module is imported
- **THEN** the class is registered as a handler for both event types

### Requirement: Auto-discovery of handler modules
The system SHALL provide an `auto_discover_handlers()` function in `infrastructure/events/registry.py` that scans the `infrastructure/events/handlers/` package using `pkgutil.walk_packages` and imports all modules. This triggers `@handles()` decorators to populate the registry. This function MUST be called at application startup.

#### Scenario: New handler auto-discovered
- **GIVEN** a new Python module in `infrastructure/events/handlers/` containing a `@handles`-decorated class
- **WHEN** `auto_discover_handlers()` runs at startup
- **THEN** the handler is registered without any manual import or wiring

### Requirement: Dispatcher resolves handlers from DI container
The `InProcessEventDispatcher` SHALL receive a Dishka `AsyncContainer` and for each dispatched event: look up handler classes from the registry, resolve each from the container, and call `handle(event)`.

#### Scenario: Handler with dependencies is resolved
- **GIVEN** a handler that depends on `UserRepository` in its constructor
- **WHEN** the dispatcher resolves the handler from the container
- **THEN** the handler receives the repository instance via DI

#### Scenario: No handlers registered for event type
- **WHEN** an event is dispatched and no handlers are registered for its type
- **THEN** the event is silently ignored (no error raised)

### Requirement: Concurrent dispatch with error isolation
The dispatcher SHALL invoke all handlers for a given event concurrently using `asyncio.gather(*tasks, return_exceptions=True)`. If any handler raises an exception, it MUST be logged and swallowed — it MUST NOT prevent other handlers from executing.

#### Scenario: Concurrent execution
- **GIVEN** two handlers registered for `UserCreated`
- **WHEN** a `UserCreated` event is dispatched
- **THEN** both handlers are invoked concurrently via `asyncio.gather`

#### Scenario: Error isolation
- **GIVEN** two handlers registered for `UserCreated`, one of which raises an exception
- **WHEN** a `UserCreated` event is dispatched
- **THEN** the failing handler's error is logged
- **AND** the other handler completes successfully

### Requirement: Handler classes registered in Dishka
Each concrete event handler class SHALL be registered in a Dishka `Provider` (`EventHandlerProvider`) with `Scope.REQUEST` so that Dishka can resolve them with their dependencies.

#### Scenario: Handler DI registration
- **GIVEN** `LogUserCreated` is registered in `EventHandlerProvider`
- **WHEN** the container resolves `LogUserCreated`
- **THEN** the instance is created with all constructor dependencies injected

## MODIFIED Requirements

### Requirement: In-process event dispatcher (updated)
The `InProcessEventDispatcher` SHALL route events to registered handlers instead of only logging them. It still logs each dispatched event for debug purposes, but additionally resolves and invokes all matching handlers concurrently.

#### Scenario: Dispatcher invokes registered handlers
- **WHEN** a `UserCreated` event is dispatched
- **THEN** all handlers registered for `UserCreated` are invoked concurrently with the event

#### Scenario: Dispatcher still logs events
- **WHEN** any event is dispatched
- **THEN** the event type and ID are logged at DEBUG level (existing behavior preserved)
