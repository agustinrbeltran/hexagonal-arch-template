## 1. Domain — Value Objects

- [x] 1.1 Add `FirstName` value object to `core/domain/profile/value_objects.py` (1–50 chars, non-empty, raises `DomainTypeError`)
- [x] 1.2 Add `LastName` value object to `core/domain/profile/value_objects.py` (1–50 chars, non-empty, raises `DomainTypeError`)
- [x] 1.3 Add `BirthDate` value object to `core/domain/profile/value_objects.py` (wraps `datetime.date`, must be past, ≤ 150 years ago, raises `DomainTypeError`)
- [x] 1.4 Write unit tests for `FirstName`, `LastName`, `BirthDate` value objects (valid/invalid scenarios)

## 2. Domain — Profile Aggregate

- [x] 2.1 Add `first_name: FirstName | None`, `last_name: LastName | None`, `birth_date: BirthDate | None` fields to `Profile.__init__` and `Profile.create`
- [x] 2.2 Add `ProfileUpdated` event to `core/domain/profile/events.py` with before/after fields for all mutable fields
- [x] 2.3 Implement `Profile.update(first_name, last_name, birth_date, username)` method that overrides all mutable fields and registers `ProfileUpdated` when any field changes (idempotent if no change)
- [x] 2.4 Write unit tests for `Profile.update` (full update, clear fields, idempotent, partial scenarios)
- [x] 2.5 Update existing `Profile.create` tests to account for new optional fields defaulting to `None`

## 3. Database Migration

- [x] 3.1 Write Supabase migration adding `first_name VARCHAR(50)`, `last_name VARCHAR(50)`, `birth_date DATE` nullable columns to `profiles` table
- [x] 3.2 Apply migration to local Supabase (`make reset.db` or `supabase db push`)

## 4. Infrastructure — Persistence

- [x] 4.1 Update SQLAlchemy imperative mapping in `core/infrastructure/persistence/mappers/profile.py` to include the three new columns
- [x] 4.2 Update `ProfileConverter` in `core/infrastructure/persistence/converters/profile_converter.py` to map new fields to/from the domain entity

## 5. Application — update_profile Use Case

- [x] 5.1 Create `core/application/update_profile/command.py` with `UpdateProfileCommand(first_name: str | None, last_name: str | None, birth_date: date | None, username: str | None)`
- [x] 5.2 Create `core/application/update_profile/port.py` with `UpdateProfileUseCase` protocol
- [x] 5.3 Create `core/application/update_profile/handler.py` with `UpdateProfileHandler` (fetch by account_id, build VOs, call `profile.update`, save, dispatch)
- [x] 5.4 Write unit tests for `UpdateProfileHandler` (success, domain error, profile not found, username conflict)

## 6. Infrastructure — HTTP Controllers & Router

- [x] 6.1 Change HTTP verb in `core/infrastructure/http/controllers/set_username.py` from `router.put("/me/username", ...)` to `router.patch("/me/username", ...)`
- [x] 6.2 Create `core/infrastructure/http/controllers/update_profile.py` with `PUT /me` endpoint wired to `UpdateProfileUseCase`
- [x] 6.3 Register `create_update_profile_router()` in `core/infrastructure/http/routers/profile_router.py` and remove any leftover `set_username` PUT reference
- [x] 6.4 Register `UpdateProfileHandler` and `UpdateProfileUseCase` in the DI providers (`shared/infrastructure/config/di/application.py` or appropriate provider)

## 7. DI Registration

- [x] 7.1 Add `UpdateProfileUseCase` / `UpdateProfileHandler` binding to the DI container
- [x] 7.2 Verify `get_my_profile` response includes the three new fields (update response schema if applicable)

## 8. Tests

- [x] 8.1 Write integration or controller-level tests for `PUT /api/v1/profiles/me` (success, validation error, auth error, conflict)
- [x] 8.2 Write integration or controller-level tests for `PATCH /api/v1/profiles/me/username` (success, conflict, auth error)
- [x] 8.3 Confirm `PUT /api/v1/profiles/me/username` no longer exists (404 or removed from router)
- [x] 8.4 Run full test suite and resolve any failures (`make code.test`)
