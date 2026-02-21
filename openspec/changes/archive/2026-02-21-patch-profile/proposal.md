## Why

The existing `PATCH /profiles/me` endpoint shares the same use case as `PUT /profiles/me`, meaning partial updates overwrite omitted fields with `NULL`. Sending only `{"first_name": "Andres"}` silently clears `last_name`, `birth_date`, and `username`.

## What Changes

- Introduce a dedicated `PatchProfileUseCase` / `PatchProfileHandler` for PATCH semantics (merge, not replace).
- Add `UNSET` sentinel to `shared/domain/` to distinguish "field not provided" from "field explicitly set to null".
- Add `profile.apply_patch()` method to the `Profile` aggregate, which only mutates and registers events for fields that are not `UNSET`.
- Introduce new `ProfilePatchApplied` domain event carrying only the delta (changed fields).
- Wire the `PATCH /profiles/me` controller to the new use case; `PUT /profiles/me` continues to use the existing `UpdateProfileUseCase` unchanged.

## Capabilities

### New Capabilities
- `patch-profile`: Partial update of a user's profile via PATCH, preserving fields not included in the request body.

### Modified Capabilities
- `profile-aggregate`: `Profile` aggregate gains `apply_patch()` method and `ProfilePatchApplied` event.

## Impact

- **New files**: `shared/domain/unset.py`, `core/application/patch_profile/{command,port,handler}.py`
- **Modified files**: `core/domain/profile/entity.py`, `core/domain/profile/events.py`, `core/infrastructure/http/controllers/update_profile.py`, DI application provider
- **API**: `PATCH /profiles/me` behavior changes (breaking fix — was incorrectly nulling fields)
- **No changes** to `PUT /profiles/me`, existing `UpdateProfileUseCase`, or `profile.update()`
