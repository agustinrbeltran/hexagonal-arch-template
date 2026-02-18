## 1. Application Layer — EventHandler Protocol

- [x] 1.1 Create `application/shared/event_handler.py` with `EventHandler[E]` protocol: generic over `DomainEvent` subtype, single async `handle(self, event: E) -> None` method

## 2. Infrastructure — Event Registry

- [x] 2.1 Create `infrastructure/events/registry.py` with:
  - Module-level `_registry: dict[type[DomainEvent], list[type]]`
  - `handles(*event_types)` class decorator that appends the class to `_registry` for each event type
  - `get_handlers_for(event_type: type[DomainEvent]) -> list[type]` lookup function
  - `auto_discover_handlers()` function using `pkgutil.walk_packages` to import all modules in `infrastructure/events/handlers/`

## 3. Infrastructure — Rewrite InProcessEventDispatcher

- [x] 3.1 Update `infrastructure/events/in_process_dispatcher.py`:
  - Constructor receives Dishka `AsyncContainer`
  - `dispatch(events)` iterates events, looks up handler types from registry, resolves each from container, invokes `handle(event)` concurrently via `asyncio.gather(*tasks, return_exceptions=True)`
  - Log and swallow exceptions from individual handlers
  - Preserve existing debug logging of event type and ID

## 4. Infrastructure — Sample Handler

- [x] 4.1 Create `infrastructure/events/handlers/__init__.py` (empty, marks package for auto-discovery scanning)
- [x] 4.2 Create `infrastructure/events/handlers/user_handlers.py` with a sample `@handles(UserCreated)` handler that logs the event (demonstrates the pattern, can be replaced with real handlers later)

## 5. DI Wiring

- [x] 5.1 Create `infrastructure/config/di/events.py` with `EventHandlerProvider` (Dishka Provider, `Scope.REQUEST`) registering all concrete handler classes
- [x] 5.2 Update `infrastructure/config/di/application.py` — change `InProcessEventDispatcher` provider to inject `AsyncContainer`
- [x] 5.3 Update `infrastructure/config/di/provider_registry.py` — add `EventHandlerProvider` to the provider list
- [x] 5.4 Call `auto_discover_handlers()` at application startup (in the app factory or DI setup)

## 6. Verification

- [x] 6.1 Run the application and verify domain events are dispatched to the sample handler (check logs)
- [x] 6.2 Run existing tests — ensure no regressions
