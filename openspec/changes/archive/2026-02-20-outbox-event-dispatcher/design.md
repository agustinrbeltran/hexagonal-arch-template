## Context

The system currently dispatches domain events in-process via `InProcessEventDispatcher`, which resolves handlers from Dishka and executes them with `asyncio.gather` within the HTTP request lifecycle. Events are dispatched *after* the unit of work commits, creating a window where events can be lost if the process crashes. All handlers share the request-scoped DI container.

Two bounded contexts produce events (Account, Core) and two event handlers exist today: `LogAccountCreated` (logging) and `CreateProfileOnAccountCreated` (cross-context state mutation via `CoreUnitOfWork`).

All use case handlers, repositories, and units of work are `Scope.REQUEST` in Dishka. Both `AccountUnitOfWork` and `CoreUnitOfWork` use the same `MainAsyncSession` type. The app-level `AsyncContainer` is available via `app.state.dishka_container`.

## Goals / Non-Goals

**Goals:**
- Decouple event handler execution from the HTTP request lifecycle
- Guarantee event durability — events persisted atomically with aggregate state
- Support retry with max attempts for failed handlers
- Keep the `EventDispatcher` protocol unchanged
- Keep existing handler implementations unchanged

**Non-Goals:**
- External message broker (Kafka, RabbitMQ, Redis Streams) — polling is sufficient for now
- Exactly-once delivery guarantees — at-least-once with idempotent handlers is acceptable
- Dead-letter queue table — failed events stay in the outbox with `delivered = false` after max retries (logged)
- Separate worker process — relay runs in-process as an asyncio task

## Decisions

### 1. Outbox table in the same database

Write outbox entries to the same PostgreSQL database using the same `MainAsyncSession`, ensuring they participate in the same transaction as the aggregate mutation.

**Alternative**: Separate event store database — rejected because it can't share transactions with the aggregate, defeating the atomicity goal.

### 2. OutboxEventDispatcher writes to session, does not commit

The dispatcher calls `session.add(OutboxRecord(...))` for each event. It does NOT flush or commit. The use case handler's UoW commit handles both the aggregate and outbox writes atomically.

**Alternative**: Dispatcher does its own flush — rejected because it would break the UoW's control over the transaction boundary.

### 3. Dispatch before commit in use case handlers

Use case handlers call `event_dispatcher.dispatch(events)` before `unit_of_work.commit()`. This ensures outbox rows are in the session when the commit happens.

**Alternative**: Keep dispatch after commit and write to outbox in a separate transaction — rejected because it reintroduces the crash window.

### 4. Polling relay as in-process asyncio task

The relay runs as a long-lived `asyncio.create_task()` started in the FastAPI lifespan. It polls every 30 seconds, processes undelivered entries, and creates isolated Dishka child scopes per handler execution.

**Alternative**: PostgreSQL LISTEN/NOTIFY — more responsive but adds complexity. Polling at 30s is acceptable for the current handler set and can be changed later.

### 5. Relay uses app-level container for child scopes

The relay holds a reference to the app-level `AsyncContainer` and creates `Scope.REQUEST` child scopes per handler invocation. Each handler gets its own `MainAsyncSession`, UoW, and repository — fully isolated from each other and from HTTP requests.

**Alternative**: Share a single session across all handlers in a poll cycle — rejected because handler failures would cascade.

### 6. Event type registry via @handles decorator

Extend the existing `@handles` decorator to also register the event class in a `dict[str, type[DomainEvent]]` mapping (event type name → class). The relay uses this to deserialize outbox payloads back into domain event instances.

**Alternative**: Separate decorator or manual registration — rejected because every event type we care about already passes through `@handles`.

### 7. Retry with max attempts, then log and stop

On handler failure, the relay increments `retry_count` on the outbox entry. When `retry_count >= max_retries`, the entry is left as `delivered = false` and a critical-level log is emitted. It is not retried again.

**Alternative**: Dead-letter table — adds complexity for no clear benefit at this scale. The outbox table itself serves as the record of failed deliveries.

### 8. Serialization with json.dumps/json.loads and default=str

Events are frozen dataclasses with simple fields (UUID, str, datetime, enums). `json.dumps(asdict(event), default=str)` handles all types. Deserialization reconstructs the event class from the type registry with type coercion for UUIDs and datetimes.

### 9. Graceful shutdown via CancelledError

The relay catches `asyncio.CancelledError` during its poll loop and exits cleanly. The lifespan cancels the relay task before closing the Dishka container.

## Risks / Trade-offs

- **[Eventual consistency]** Handlers now execute asynchronously (up to 30s delay). Any flow that implicitly relied on handlers completing within the request will behave differently. → Mitigation: Current handlers (profile creation, logging) tolerate delay. Document this for future handler authors.

- **[Outbox table growth]** Delivered entries accumulate indefinitely. → Mitigation: Add a periodic cleanup (not in this change). Delivered entries are inert and the index only covers `delivered = false`.

- **[Polling overhead]** One query every 30 seconds even when idle. → Mitigation: Negligible for a single index scan on a small table. Can move to NOTIFY later if needed.

- **[Handler idempotency]** At-least-once delivery means handlers may be called more than once on retries. → Mitigation: `CreateProfileOnAccountCreated` will fail with a unique constraint on duplicate — acceptable. `LogAccountCreated` is naturally idempotent. Future handlers should be designed for idempotency.

- **[Enum deserialization]** Enum values are serialized as strings via `default=str`. Deserialization needs to reconstruct the correct enum type. → Mitigation: Handle in the deserialization utility with explicit type annotation inspection from the dataclass fields.
