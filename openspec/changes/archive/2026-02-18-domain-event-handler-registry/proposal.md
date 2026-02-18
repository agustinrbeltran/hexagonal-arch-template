## Why

The `InProcessEventDispatcher` currently only logs domain events — it has no mechanism to route events to actual handlers. Every use case handler already collects events from aggregates and dispatches them post-commit, but nothing is listening. To close this loop, we need a handler registry that maps `DomainEvent` subclasses to async handler callables, populated implicitly via decorators and auto-discovery rather than manual wiring.

## What Changes

- Introduce an `EventHandler[E]` protocol in the application layer as a port for event handlers
- Create a `@handles(EventType)` decorator that auto-registers handler classes in a module-level registry
- Implement auto-discovery of handler modules via `importlib`/`pkgutil` scanning of a `handlers/` package
- Rewrite `InProcessEventDispatcher` to look up registered handlers by event type, resolve them from Dishka, and invoke them concurrently with `asyncio.gather`
- Errors in individual handlers are logged and swallowed — all handlers execute regardless of failures
- Unhandled event types (no registered handlers) are silently ignored (existing behavior)

## Capabilities

### New Capabilities

- `domain-event-handler-registry`: Decorator-based auto-registration of domain event handlers with DI-resolved class instances and concurrent dispatch

### Modified Capabilities

- `domain-events`: The existing `EventDispatcher` port and `InProcessEventDispatcher` implementation gain actual handler routing instead of log-only behavior

## Impact

- **Application layer**: New `EventHandler[E]` protocol in `application/shared/`
- **Infrastructure layer**: New `infrastructure/events/registry.py`, new `infrastructure/events/handlers/` package, rewritten `InProcessEventDispatcher`
- **DI configuration**: `InProcessEventDispatcher` needs access to the Dishka container (or a factory) to resolve handler instances
- **No API changes**: This is an internal infrastructure enhancement
- **No database changes**: No migrations required
- **No breaking changes**: Existing dispatch calls continue to work; handlers are additive
