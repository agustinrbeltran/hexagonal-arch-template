## Why

Two bugs prevent the `set_username` use case from working correctly: the username is never persisted to the database because `save()` is never called, and the `UsernameChanged` event can't be replayed by the outbox relay because event type registration is coupled exclusively to handler registration — events without handlers are unknown to the deserializer.

## What Changes

- Add `@register_event` decorator to `shared/infrastructure/events/registry.py` that registers an event class in `_event_type_registry` independently of any handler
- Apply `@register_event` to `UsernameChanged` (and `ProfileCreated`) in `core/domain/profile/events.py` so they are always known to the relay
- Change `SqlaProfileRepository.save()` to use `session.merge()` instead of `session.add()`, giving it upsert semantics that work for both INSERT and UPDATE
- Call `self._profile_repository.save(profile)` in `SetUsernameHandler.execute()` before dispatching events

## Capabilities

### New Capabilities
- `event-type-registration`: Mechanism to register domain event types in the deserializer registry independently of handler registration, so events without handlers can still be serialized/deserialized via the outbox

### Modified Capabilities
- `profile-aggregate`: `save()` on `SqlaProfileRepository` now has upsert (merge) semantics; `set_username` use case now correctly persists the updated profile

## Impact

- `src/shared/infrastructure/events/registry.py` — new `@register_event` decorator
- `src/core/domain/profile/events.py` — apply `@register_event` to `ProfileCreated` and `UsernameChanged`
- `src/core/infrastructure/persistence/sqla_profile_repository.py` — `save()` uses `session.merge()`
- `src/core/application/set_username/handler.py` — add `save()` call
- Existing tests for `ProfileRepository.save()` and `SetUsernameHandler` may need updating
