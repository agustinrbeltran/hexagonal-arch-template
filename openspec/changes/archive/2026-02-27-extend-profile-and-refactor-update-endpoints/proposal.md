## Why

The Profile aggregate currently holds only a `username`, leaving no place to store basic personal information such as name and birth date. As the application grows, a richer profile is needed. The existing `PUT /api/v1/profiles/me/username` endpoint is also too narrow — it forces multiple round-trips when a user wants to update several fields at once.

## What Changes

- Add optional fields to the `Profile` aggregate: `first_name`, `last_name`, `birth_date`
- Add corresponding value objects: `FirstName`, `LastName`, `BirthDate`
- Add domain methods on `Profile` to update each field and register appropriate events
- Add `ProfileUpdated` domain event capturing the changed fields
- **BREAKING** Remove `PUT /api/v1/profiles/me/username` endpoint
- Add `PUT /api/v1/profiles/me` — full profile update (overrides all mutable fields; null resets optional ones)
- Add `PATCH /api/v1/profiles/me/username` — partial username-only update (keeps existing behaviour but under the PATCH verb)
- Extend `update_profile` use case (or introduce it) to handle the full-update path
- Extend `set_username` use case to remain available for the PATCH path
- Database migration: add `first_name`, `last_name`, `birth_date` columns to the `profiles` table

## Capabilities

### New Capabilities
<!-- none — all changes are extensions to an existing capability -->

### Modified Capabilities
- `profile-aggregate`: adding optional `first_name`, `last_name`, `birth_date` fields, new value objects, new domain methods, and a new `ProfileUpdated` event; also capturing the updated HTTP API contract (PUT /me replaces PUT /me/username, PATCH /me/username added)

## Impact

- `core/domain/profile/` — entity, value objects, events, errors
- `core/application/` — new `update_profile` use case; `set_username` use case unchanged in logic
- `core/infrastructure/` — SQLAlchemy mapping, repository, HTTP controllers/routers
- Database schema — `profiles` table gains three nullable columns
- API clients — `PUT /api/v1/profiles/me/username` removed (breaking); two new endpoints added
