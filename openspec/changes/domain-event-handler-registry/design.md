## Context

The `InProcessEventDispatcher` currently only logs domain events — it never routes them to handlers. Every use case handler already calls `event_dispatcher.dispatch(aggregate.collect_events())` after committing via the unit of work, but the dispatcher is a dead end. We need to close this loop with a registry that maps event types to handler classes, resolved via Dishka DI, and invoked concurrently.

The existing Dishka DI container is used throughout the project for port → adapter wiring (see `infrastructure/config/di/application.py`). The `EventDispatcher` protocol lives in `application/shared/event_dispatcher.py`.

## Goals / Non-Goals

**Goals:**
- Auto-register event handlers via a `@handles(EventType)` class decorator
- Auto-discover handler modules by scanning a `handlers/` package at startup
- Resolve handler instances from Dishka so handlers can receive injected dependencies
- Dispatch concurrently with `asyncio.gather` — fire-and-forget semantics
- Log and swallow individual handler errors — never block other handlers
- Silently ignore events with no registered handlers (current behavior preserved)

**Non-Goals:**
- Retry mechanisms (log-only for now; retry can be added later)
- Ordering guarantees between handlers
- Transactional handlers (dispatch is already post-commit)
- Persistent event store or outbox pattern
- External event bus (Kafka, RabbitMQ, etc.)

## Decisions

### 1. Handler protocol in application layer, implementations in infrastructure

**Decision**: Define `EventHandler[E]` as a `Protocol` in `application/shared/event_handler.py`. Concrete handlers live in `infrastructure/events/handlers/`.

**Rationale**: Follows the existing hexagonal pattern — ports in application, adapters in infrastructure. The domain layer is untouched. Use case handlers only depend on the `EventDispatcher` port, never on individual event handlers.

### 2. Module-level registry with `@handles()` decorator

**Decision**: A module-level `dict[type[DomainEvent], list[type[EventHandler]]]` in `infrastructure/events/registry.py`, populated by a `@handles(EventType)` class decorator.

**Rationale**: This is the simplest pattern that achieves auto-registration. No framework dependency, no metaclass magic. The decorator is explicit — you see at a glance what event a handler responds to. A handler class can be decorated with multiple `@handles(...)` for multiple event types.

**Alternative considered**: Dishka's `provide_all` for `list[EventHandler[T]]`. Rejected because Dishka doesn't natively support collecting all implementations of a generic protocol into a list, and building a custom Dishka decorator would add complexity for no clear benefit.

### 3. Auto-discovery via `pkgutil` + `importlib`

**Decision**: At application startup (during DI container setup), call `auto_discover_handlers()` which scans `infrastructure/events/handlers/` using `pkgutil.walk_packages` and imports each module. The import triggers `@handles()` decorators which populate the registry.

**Rationale**: Adding a new handler is just: create a file in `handlers/`, decorate the class. No manual import needed. This mirrors Spring's `@EventListener` component scanning.

### 4. Dispatcher resolves handlers from Dishka `AsyncContainer`

**Decision**: `InProcessEventDispatcher` receives a Dishka `AsyncContainer` and for each event, looks up handler classes in the registry, resolves each from the container, and calls `handle(event)`.

**Rationale**: Handlers get full DI support — they can depend on repositories, services, etc. The container is scoped per-request (Dishka's `Scope.REQUEST`), so handlers share the same session/UoW as the use case that triggered the event. However, since dispatch happens post-commit, there's no transactional coupling.

**Implementation detail**: The dispatcher needs access to the request-scoped container. Since it's already resolved within a request scope, it can receive the container as a constructor dependency. Dishka supports self-injection of the container.

### 5. Concurrent dispatch with error isolation

**Decision**: For each event, gather all handler invocations with `asyncio.gather(*tasks, return_exceptions=True)`. Log any exceptions but never propagate them.

**Rationale**: Fire-and-forget semantics. A failing email handler must never prevent an audit-log handler from running. All handlers execute regardless of individual failures.

### 6. Event handler classes are registered in Dishka as REQUEST-scoped

**Decision**: Each concrete handler class is registered in a new `EventHandlerProvider` (Dishka `Provider`) in `infrastructure/config/di/events.py`. This allows Dishka to resolve them with their dependencies.

**Rationale**: Handlers may need repositories, services, or other request-scoped dependencies. Registering them in Dishka gives them access to the full DI graph. The `@handles()` decorator registers the event-type mapping; Dishka registration provides the DI wiring.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Application Layer                                           │
│                                                              │
│  EventHandler[E] (Protocol)     EventDispatcher (Protocol)   │
│    handle(event: E) -> None       dispatch(events) -> None   │
└──────┬───────────────────────────────────┬───────────────────┘
       │                                   │
┌──────▼───────────────────────────────────▼───────────────────┐
│  Infrastructure Layer                                        │
│                                                              │
│  registry.py                                                 │
│    _registry: dict[type[DomainEvent], list[type]]            │
│    @handles(EventType) ─── class decorator                   │
│    get_handlers_for(event_type) → list[type]                 │
│    auto_discover_handlers() ─── pkgutil scan                 │
│                                                              │
│  in_process_dispatcher.py                                    │
│    InProcessEventDispatcher(container: AsyncContainer)       │
│      dispatch(events):                                       │
│        for event in events:                                  │
│          handler_types = registry.get_handlers_for(type(ev)) │
│          handlers = [container.get(ht) for ht in ...]        │
│          await asyncio.gather(                               │
│            *[h.handle(event) for h in handlers],             │
│            return_exceptions=True                            │
│          )                                                   │
│          ─── log exceptions, never propagate ───             │
│                                                              │
│  handlers/                                                   │
│    __init__.py  (empty, marks package for scanning)          │
│    user_handlers.py                                          │
│      @handles(UserCreated)                                   │
│      class LogUserCreated(EventHandler[UserCreated]):        │
│        async def handle(self, event): log.info(...)          │
│                                                              │
│  config/di/events.py                                         │
│    EventHandlerProvider (Dishka Provider)                    │
│      ─── registers concrete handler classes ───              │
└──────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

**[Risk] Auto-discovery hides handler registration** → Mitigated by the `@handles()` decorator being explicit on each class. A grep for `@handles` shows all registrations. Trade-off accepted for reduced boilerplate.

**[Risk] Container resolution failure at dispatch time** → If a handler class isn't registered in Dishka, resolution will fail. Mitigated by logging the error and continuing (error isolation). Could add a startup validation step later.

**[Trade-off] Dishka container passed to dispatcher** → Slight service-locator smell, but the alternative (pre-resolving all possible handlers) doesn't work with request-scoped dependencies. This is a pragmatic compromise.

**[Trade-off] No retry mechanism** → Failures are logged and lost. Acceptable for a template project; a retry/dead-letter mechanism can be layered on later without changing the handler interface.

## Open Questions

None — all decisions resolved during exploration.
