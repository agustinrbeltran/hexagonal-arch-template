## 1. Database & Persistence

- [ ] 1.1 Create Supabase migration for `outbox` table with partial index on `occurred_at WHERE delivered = false`
- [ ] 1.2 Create `OutboxRecord` dataclass and imperative mapper in `shared/infrastructure/persistence/mappers/outbox.py`
- [ ] 1.3 Register `map_outbox_table()` in `app_factory.py` `_map_tables()`

## 2. Event Serialization

- [ ] 2.1 Create `shared/infrastructure/events/serialization.py` with `serialize_event()` and `deserialize_event()` functions
- [ ] 2.2 Extend `@handles` decorator in `registry.py` to populate an event type name registry (`str -> type[DomainEvent]`)
- [ ] 2.3 Add `get_event_class(name: str)` function to `registry.py`

## 3. Outbox Dispatcher

- [ ] 3.1 Replace `InProcessEventDispatcher` with `OutboxEventDispatcher` in `shared/infrastructure/events/dispatcher.py` (accepts `MainAsyncSession`, writes `OutboxRecord`s to session)
- [ ] 3.2 Update DI provider in `application.py` to wire `OutboxEventDispatcher` with `MainAsyncSession` instead of `AsyncContainer`

## 4. Polling Relay

- [ ] 4.1 Create `OutboxRelay` in `shared/infrastructure/events/relay.py` with poll loop, event deserialization, handler resolution via Dishka child scopes, and delivery marking
- [ ] 4.2 Implement retry logic: increment `retry_count` on failure, skip entries at max retries with critical log
- [ ] 4.3 Implement graceful shutdown via `CancelledError` handling

## 5. App Lifecycle & DI Wiring

- [ ] 5.1 Start relay as `asyncio.create_task()` in FastAPI lifespan, cancel on shutdown
- [ ] 5.2 Wire relay dependencies (app container, session factory, relay config) in DI or lifespan

## 6. Use Case Handler Reordering

- [ ] 6.1 Swap dispatch/commit ordering in `account/application/sign_up/handler.py`
- [ ] 6.2 Swap dispatch/commit ordering in `account/application/create_account/handler.py`
- [ ] 6.3 Swap dispatch/commit ordering in `account/application/activate_account/handler.py`
- [ ] 6.4 Swap dispatch/commit ordering in `account/application/deactivate_account/handler.py`
- [ ] 6.5 Swap dispatch/commit ordering in `account/application/set_account_password/handler.py`
- [ ] 6.6 Swap dispatch/commit ordering in `account/application/grant_admin/handler.py`
- [ ] 6.7 Swap dispatch/commit ordering in `account/application/revoke_admin/handler.py`
- [ ] 6.8 Swap dispatch/commit ordering in `core/application/set_username/handler.py`

## 7. Tests

- [ ] 7.1 Unit tests for `serialize_event()` and `deserialize_event()` with all field types (UUID, datetime, enum, str)
- [ ] 7.2 Unit tests for `OutboxEventDispatcher` (adds records to session, does not commit)
- [ ] 7.3 Unit tests for event type registry (`get_event_class`, `@handles` populates both registries)
- [ ] 7.4 Unit tests for `OutboxRelay` (processes entries, retries on failure, skips max retries, graceful shutdown)
- [ ] 7.5 Verify existing tests pass with dispatch/commit reordering (run full test suite)
