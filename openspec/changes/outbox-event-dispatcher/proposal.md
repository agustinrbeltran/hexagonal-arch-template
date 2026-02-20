## Why

The current `InProcessEventDispatcher` executes all event handlers synchronously within the HTTP request lifecycle. This means the caller (use case handler) blocks until every handler finishes, coupling bounded contexts at the request level. As the number of cross-context event handlers grows, this erodes aggregate consistency boundaries and increases response latency. Additionally, events are dispatched *after* commit — if the process crashes between commit and dispatch, events are lost.

## What Changes

- Replace `InProcessEventDispatcher` with `OutboxEventDispatcher` that writes events to an `outbox` table within the same DB transaction as the aggregate mutation (atomic guarantee).
- Add an `outbox` PostgreSQL table with delivery tracking and retry support.
- Add event serialization/deserialization utilities (`json.dumps`/`json.loads`).
- Add a polling `OutboxRelay` that runs as a background `asyncio.Task`, reads undelivered events every 30 seconds, resolves handlers via Dishka child scopes, and marks events as delivered.
- Add an event type registry (event class name → event class) for deserialization, piggybacking on the existing `@handles` decorator.
- **Swap dispatch/commit ordering** in all 8 use case handlers: `dispatch()` now happens *before* `commit()` so outbox rows are part of the same transaction.
- **BREAKING**: `InProcessEventDispatcher` is removed. The `EventDispatcher` protocol is unchanged.

## Capabilities

### New Capabilities
- `outbox-event-dispatcher`: Covers the outbox table, `OutboxEventDispatcher` implementation, event serialization, the polling relay, retry/max-retry logic, graceful shutdown, and DI wiring.

### Modified Capabilities
- `domain-events`: The dispatch ordering requirement changes from "after commit" to "before commit" (outbox rows written in same TX). The dispatcher implementation changes from in-process to outbox-based.
- `domain-event-handler-registry`: The registry gains an event type name → class mapping for deserialization. Handlers are now invoked by the relay instead of the dispatcher.

## Impact

- **Database**: New `outbox` table + index (Supabase migration).
- **Persistence layer**: New `OutboxRecord` dataclass + SQLAlchemy imperative mapper in `shared/infrastructure/persistence/mappers/outbox.py`.
- **Events infrastructure**: `shared/infrastructure/events/dispatcher.py` rewritten, new `serialization.py` and `relay.py`.
- **Registry**: `shared/infrastructure/events/registry.py` extended with event type class mapping.
- **DI**: `shared/infrastructure/config/di/application.py` rewired for `OutboxEventDispatcher` (takes `MainAsyncSession` instead of `AsyncContainer`).
- **App lifecycle**: `shared/infrastructure/config/app_factory.py` starts relay task in lifespan, maps outbox table.
- **8 use case handlers**: Mechanical swap of dispatch/commit ordering (account: sign_up, create_account, activate_account, deactivate_account, set_account_password, grant_admin, revoke_admin; core: set_username).
- **Existing handler implementations**: Unchanged (`CreateProfileOnAccountCreated`, `LogAccountCreated`).
