## Context

The outbox relay deserializes events by looking up `event_type` (a string class name) in `_event_type_registry`. That registry is populated exclusively as a side-effect of the `@handles` decorator — meaning only event types that have at least one handler ever become known to the deserializer. `UsernameChanged` is emitted to the outbox but has no handler yet, so the relay raises `ValueError: Unknown event type: UsernameChanged` and increments retry_count until the entry is abandoned.

Separately, `SetUsernameHandler` loads a `Profile`, mutates it in memory via `set_username()`, dispatches events, then commits — but never calls `repository.save()`. The SQLAlchemy session has no knowledge of the in-memory change and nothing is flushed for the profile row. The username remains NULL in the database. Additionally, `SqlaProfileRepository.save()` uses `session.add()`, which only works for new (INSERT) entities; using it on an already-persisted profile would cause a duplicate PK error.

## Goals / Non-Goals

**Goals:**
- Event types can be registered for deserialization independently of whether any handler exists
- Profile username changes are durably persisted on each `set_username` call
- `save()` on `SqlaProfileRepository` works correctly for both insert (new profile) and update (existing profile)

**Non-Goals:**
- Adding a handler for `UsernameChanged` (deferred — no consumer exists yet)
- Changing the outbox relay's retry/dead-letter policy
- Modifying the `Username` value object validation rules

## Decisions

### 1. `@register_event` decorator for decoupled event type registration

**Decision**: Add a `register_event(*event_types)` function (usable as a decorator or called directly) to `shared/infrastructure/events/registry.py`. It inserts each event class into `_event_type_registry` by `__name__`, with no handler side effects.

**Rationale**: The coupling between event serialization knowledge and handler existence is the root cause. Decoupling them means any domain event can be registered at module-import time, just by decorating the event class in its own module. This is analogous to how `@handles` self-registers — the same pattern applied one layer down.

**Alternative considered**: Auto-scan all `DomainEvent` subclasses at startup. Rejected because it requires importing all domain modules at boot, introduces import-order fragility, and makes registration implicit and hard to audit.

**Alternative considered**: Store the event class reference on the `DomainEvent` base itself (class registry pattern). Rejected because it couples shared kernel to concrete subclasses.

### 2. `session.merge()` for upsert semantics in `SqlaProfileRepository.save()`

**Decision**: Replace `session.add(record)` with `session.merge(record)` in `save()`. `merge()` performs an identity-map lookup: if the PK is already tracked in the session, it updates that instance; if not, it issues a SELECT then UPDATE (or INSERT if genuinely new).

**Rationale**: The repository's `save()` method is the single persistence point for Profile entities. It should work regardless of whether the profile is new or existing — the caller (use case handler) should not need to know which. `merge()` is the standard SQLAlchemy idiom for this pattern with imperative-mapped detached objects.

**Alternative considered**: Separate `update()` method on the repository, handler calls `save()` for new profiles and `update()` for existing ones. Rejected — adds complexity and requires the handler to track entity lifecycle state, which is an infrastructure concern leaking into the application layer.

**Trade-off**: `merge()` may issue an extra SELECT if the record is not already in the session's identity map. For the profile update path this is one extra query per request — acceptable.

### 3. Call `save()` before `dispatch()` in `SetUsernameHandler`

**Decision**: Add `self._profile_repository.save(profile)` in `SetUsernameHandler.execute()` between the `set_username()` call and `event_dispatcher.dispatch()`.

**Rationale**: Follows the established pattern from `CreateProfileHandler` — mutate aggregate, save to repo, dispatch events, commit. The save must happen before commit (which includes the flush). Dispatch before commit is required by the outbox pattern (atomic write of aggregate state + outbox entry).

## Risks / Trade-offs

- **`session.merge()` SELECT overhead**: One extra DB round-trip on profile update. Acceptable at current scale; can be optimized with explicit UPDATE statement if needed later.
- **`@register_event` must be called at import time**: If an event module is never imported (e.g., a bounded context is not loaded), its events remain unregistered. Mitigated by the fact that `auto_discover_handlers()` already imports all handler packages, and event modules are imported transitively. The `@register_event` decorator on the event class itself ensures registration happens when the domain module is first imported.
- **Existing outbox entries with `UsernameChanged`**: Entries already in the database with `retry_count > 0` will be retried once the fix is deployed. They will deserialize correctly but find no handlers — the relay will mark them delivered (correct behavior per existing spec: "no handlers → mark delivered").
