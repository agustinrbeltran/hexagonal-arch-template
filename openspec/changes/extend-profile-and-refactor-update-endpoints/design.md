## Context

The `core` bounded context manages user profiles. `Profile` currently holds `id_`, `account_id`, and `username: Username | None`. The HTTP API exposes a single `PUT /api/v1/profiles/me/username` for username updates, using the `SetUsernameUseCase`.

The application now needs richer profile data (name, birth date) and a more ergonomic API that lets a client update all mutable profile fields in one request.

## Goals / Non-Goals

**Goals:**
- Add optional `first_name`, `last_name`, `birth_date` fields to the `Profile` aggregate with corresponding value objects
- Introduce an `update_profile` use case backing `PUT /api/v1/profiles/me` (full override semantics)
- Migrate the existing `set_username` controller from `PUT /me/username` → `PATCH /me/username` (no application-layer changes)
- Remove the old `PUT /me/username` endpoint
- DB migration: add three nullable columns to `profiles` table

**Non-Goals:**
- Profile photo / avatar support
- Visibility or privacy settings
- Profanity filtering or advanced string sanitisation beyond basic domain invariants

## Decisions

### 1. Value objects for new fields
`FirstName` and `LastName`: frozen dataclasses wrapping a trimmed non-empty string (1–50 chars). `BirthDate`: frozen dataclass wrapping `datetime.date`, constrained to the past and no more than 150 years ago. All raise `DomainTypeError` on invalid input.

**Alternative considered**: store raw strings/dates directly on `Profile`. Rejected — value objects enforce invariants and are consistent with the existing `Username` pattern.

### 2. Single `ProfileUpdated` event for full-profile mutations
Introduce `ProfileUpdated` carrying before/after values for all mutable fields. A single event per user action keeps the outbox lean and consumers simple.

**Alternative considered**: one event per changed field (`FirstNameChanged`, etc.). Rejected — verbose, and a PUT is a single atomic user intent.

### 3. New `update_profile` use case for `PUT /api/v1/profiles/me`
`UpdateProfileCommand` accepts all mutable fields as `str | None` / `date | None`. `UpdateProfileHandler` fetches the profile by `account_id`, calls `profile.update(...)`, saves, and dispatches. `null` in the command means "clear this field".

**Alternative considered**: extend `SetUsernameHandler` to accept more fields. Rejected — violates single-responsibility and PUT vs PATCH semantics are different.

### 4. Reuse `set_username` use case unchanged for `PATCH /me/username`
The existing `SetUsernameUseCase` logic is correct. Only the HTTP controller changes (verb and path). No application-layer modification needed.

### 5. Database migration — additive only
Three nullable columns added to `profiles`: `first_name VARCHAR(50)`, `last_name VARCHAR(50)`, `birth_date DATE`. Existing rows default to NULL. No data migration required.

## Risks / Trade-offs

- [Breaking change: PUT /me/username removed] → API clients must switch to PATCH /me/username. Document in changelog / release notes.
- [PUT null-reset semantics] → Sending `null` for a field on `PUT /me` explicitly clears it. Must be clearly communicated in API docs to avoid accidental data loss.
- [Partial vs full update confusion] → Two endpoints with different semantics (PUT = full override, PATCH = username only) could confuse clients. Mitigated by clear OpenAPI descriptions and distinct paths.

## Migration Plan

1. Apply additive DB migration (nullable columns) — safe, non-destructive; can be done ahead of code deploy.
2. Deploy new code: `PUT /me` added, `PATCH /me/username` added, `PUT /me/username` removed.
3. Communicate breaking change to API consumers before deploy.

Rollback: revert code deploy and, if needed, drop the three new nullable columns (no data loss since they're new).
