## Context

The `PATCH /profiles/me` and `PUT /profiles/me` endpoints currently share the same `UpdateProfileUseCase` and handler. Both treat `None` in the command as "clear this field". Because Pydantic defaults omitted fields to `None`, a PATCH request with only `{"first_name": "Andres"}` silently nulls out `last_name`, `birth_date`, and `username`.

The root ambiguity: `None` in `UpdateProfileCommand` carries two conflicting meanings:
- "field was not included in the request" → keep current value
- "field was explicitly set to null" → clear it

## Goals / Non-Goals

**Goals:**
- PATCH semantics: only mutate fields that were explicitly included in the request body
- Clearing a field (sending `null` explicitly) MUST be supported
- `profile.apply_patch()` on the aggregate registers `ProfilePatchApplied` with only the delta
- `PUT /profiles/me` and `UpdateProfileUseCase` remain untouched

**Non-Goals:**
- Changing PUT behavior or the existing `profile.update()` method
- Changing how username uniqueness is enforced
- Adding fine-grained per-field events (single `ProfilePatchApplied` with delta is sufficient)

## Decisions

### 1. Separate `PatchProfileUseCase` (not extending `UpdateProfileCommand`)

Considered extending `UpdateProfileCommand` with a `fields_to_update: frozenset[str]` set. Rejected: bleeds HTTP/Pydantic concerns into the application layer command. A separate `PatchProfileCommand` + `PatchProfileHandler` is cleaner — each use case has a single, clear intent.

### 2. `UNSET` sentinel in `shared/domain/`

The `PatchProfileCommand` fields use type `str | None | _Unset` with a default of `UNSET`. This distinguishes three states at the domain boundary:

| Value | Meaning |
|-------|---------|
| `FirstName("Andres")` | Field explicitly set to this value |
| `None` | Field explicitly cleared (set to NULL) |
| `UNSET` | Field not included in the request — skip |

Location: `shared/domain/unset.py`. Exposes `UNSET` singleton and `_Unset` type.

Considered `model_fields_set` passed through the command. Rejected: couples the command shape to Pydantic's introspection mechanism.

### 3. Single `ProfilePatchApplied` event carrying only the delta

Each changed field is represented as a `(old_value, new_value)` tuple. Fields not touched by the patch are absent (set to `None` in the event). This keeps the event schema stable while conveying exactly what changed.

```
ProfilePatchApplied(
    profile_id=...,
    first_name=("old", "Andres"),  # changed
    last_name=None,                 # not touched
    birth_date=None,                # not touched
    username=None,                  # not touched
)
```

Fine-grained per-field events (`ProfileFirstNameChanged`, etc.) were considered but rejected as premature — no downstream consumer currently requires that granularity.

### 4. `apply_patch()` owns mutation and event registration

The handler passes only value objects (or `UNSET`) to `profile.apply_patch()`. The aggregate decides field-by-field whether a mutation happened, updates its state, and registers `ProfilePatchApplied` only if at least one field changed. This keeps business logic inside the aggregate, not in the handler.

## Risks / Trade-offs

- **mypy strict mode**: `str | None | _Unset` requires careful type annotations. The sentinel type must be exported and used consistently in command, handler, and aggregate signatures. → Use `TYPE_CHECKING` imports if needed; add to mypy known types.
- **Event with all-`None` delta fields**: If the patch payload matches current state exactly, `apply_patch()` returns without registering an event (idempotent). This is correct behavior but handlers must not assume an event is always produced. → Handler already calls `profile.collect_events()` which returns empty list safely.
