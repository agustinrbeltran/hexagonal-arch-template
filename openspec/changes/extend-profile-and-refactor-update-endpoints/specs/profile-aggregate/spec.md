## ADDED Requirements

### Requirement: FirstName value object
The `FirstName` value object SHALL be located at `core/domain/profile/value_objects.py`. It SHALL wrap a non-empty trimmed string of 1–50 characters and raise `DomainTypeError` on invalid input.

#### Scenario: Valid first name
- **WHEN** `FirstName("Alice")` is constructed
- **THEN** the value object is created successfully

#### Scenario: Empty first name
- **WHEN** `FirstName("")` is constructed
- **THEN** a `DomainTypeError` is raised

#### Scenario: First name too long
- **WHEN** `FirstName("A" * 51)` is constructed
- **THEN** a `DomainTypeError` is raised

### Requirement: LastName value object
The `LastName` value object SHALL be located at `core/domain/profile/value_objects.py`. It SHALL wrap a non-empty trimmed string of 1–50 characters and raise `DomainTypeError` on invalid input.

#### Scenario: Valid last name
- **WHEN** `LastName("Smith")` is constructed
- **THEN** the value object is created successfully

#### Scenario: Empty last name
- **WHEN** `LastName("")` is constructed
- **THEN** a `DomainTypeError` is raised

#### Scenario: Last name too long
- **WHEN** `LastName("B" * 51)` is constructed
- **THEN** a `DomainTypeError` is raised

### Requirement: BirthDate value object
The `BirthDate` value object SHALL be located at `core/domain/profile/value_objects.py`. It SHALL wrap a `datetime.date` value. The date MUST be in the past and no more than 150 years before today. It SHALL raise `DomainTypeError` on invalid input.

#### Scenario: Valid birth date
- **WHEN** `BirthDate(date(1990, 6, 15))` is constructed
- **THEN** the value object is created successfully

#### Scenario: Future birth date
- **WHEN** `BirthDate(date(2099, 1, 1))` is constructed
- **THEN** a `DomainTypeError` is raised

#### Scenario: Birth date too far in the past
- **WHEN** `BirthDate(date(1800, 1, 1))` is constructed
- **THEN** a `DomainTypeError` is raised

### Requirement: Profile full update
The Profile aggregate SHALL support an `update(first_name, last_name, birth_date, username)` method where all parameters are optional (may be `None`). The method SHALL override each field with the supplied value (including setting a field to `None` to clear it). It SHALL register a `ProfileUpdated` event if any field changes. The method SHALL be idempotent when called with the same values.

#### Scenario: Update all fields
- **WHEN** `profile.update(first_name=FirstName("Alice"), last_name=LastName("Smith"), birth_date=BirthDate(date(1990,6,15)), username=Username("alice_s"))` is called
- **THEN** all fields are updated and a `ProfileUpdated` event is registered

#### Scenario: Clear a field with None
- **WHEN** `profile.update(first_name=None, last_name=None, birth_date=None, username=None)` is called on a profile with existing values
- **THEN** all fields are set to `None` and a `ProfileUpdated` event is registered

#### Scenario: Update with same values is idempotent
- **WHEN** `profile.update(...)` is called with the exact same values already stored
- **THEN** no `ProfileUpdated` event is registered

#### Scenario: Partial update via PUT semantics
- **WHEN** `profile.update(first_name=FirstName("Bob"), last_name=None, birth_date=None, username=None)` is called
- **THEN** `first_name` is set to "Bob", all other fields are set to `None`, and a `ProfileUpdated` event is registered

### Requirement: ProfileUpdated domain event
The `ProfileUpdated` event SHALL be located at `core/domain/profile/events.py` and decorated with `@register_event`. It SHALL carry: `profile_id: UUID`, `old_first_name: str | None`, `new_first_name: str | None`, `old_last_name: str | None`, `new_last_name: str | None`, `old_birth_date: date | None`, `new_birth_date: date | None`, `old_username: str | None`, `new_username: str | None`.

#### Scenario: ProfileUpdated event fields
- **WHEN** a Profile update results in field changes
- **THEN** the `ProfileUpdated` event contains the before/after values for all mutable fields

### Requirement: update_profile use case
An `UpdateProfileHandler` SHALL be located at `core/application/update_profile/handler.py`. It SHALL accept an `UpdateProfileCommand` (located at `core/application/update_profile/command.py`) with fields: `first_name: str | None`, `last_name: str | None`, `birth_date: date | None`, `username: str | None`. The handler SHALL resolve the profile by `account_id` from the authenticated session, construct value objects for non-None fields, call `profile.update(...)`, save, and dispatch events.

#### Scenario: Full profile update persists changes
- **GIVEN** an authenticated user with an existing profile
- **WHEN** `UpdateProfileHandler.execute(UpdateProfileCommand(first_name="Alice", last_name="Smith", birth_date=date(1990,6,15), username="alice_s"))` is called
- **THEN** the profile row in the database is updated with all four field values

#### Scenario: Clearing fields with null
- **GIVEN** an authenticated user with profile fields already set
- **WHEN** `UpdateProfileHandler.execute(UpdateProfileCommand(first_name=None, last_name=None, birth_date=None, username=None))` is called
- **THEN** all mutable fields in the profile row are set to NULL

#### Scenario: Domain validation error on invalid username
- **WHEN** `UpdateProfileCommand(username="x")` is executed (too short)
- **THEN** a `DomainTypeError` is raised and no changes are persisted

### Requirement: API endpoint PUT /api/v1/profiles/me
A `PUT /api/v1/profiles/me` endpoint SHALL be located at `core/infrastructure/http/controllers/update_profile.py`. It SHALL require bearer authentication. It SHALL accept a JSON body with optional fields: `first_name`, `last_name`, `birth_date` (ISO 8601 date string), `username`. It SHALL invoke `UpdateProfileUseCase` and return `204 No Content` on success. It SHALL return `400` for domain validation errors, `401` for unauthenticated requests, `404` if profile not found, `409` for username conflicts, `503` for infrastructure errors.

#### Scenario: Successful full profile update
- **GIVEN** an authenticated user
- **WHEN** `PUT /api/v1/profiles/me` is called with `{"first_name": "Alice", "last_name": "Smith", "birth_date": "1990-06-15", "username": "alice_s"}`
- **THEN** the response is `204 No Content`

#### Scenario: Unauthenticated request
- **WHEN** `PUT /api/v1/profiles/me` is called without a bearer token
- **THEN** the response is `401 Unauthorized`

#### Scenario: Invalid field value
- **WHEN** `PUT /api/v1/profiles/me` is called with `{"username": "x"}`
- **THEN** the response is `400 Bad Request`

### Requirement: API endpoint PATCH /api/v1/profiles/me/username
A `PATCH /api/v1/profiles/me/username` endpoint SHALL be located at `core/infrastructure/http/controllers/set_username.py`. It SHALL require bearer authentication. It SHALL accept a JSON body with `username: str`. It SHALL invoke `SetUsernameUseCase` and return `204 No Content` on success. It SHALL return the same error codes as the former `PUT /me/username`.

#### Scenario: Successful username patch
- **GIVEN** an authenticated user
- **WHEN** `PATCH /api/v1/profiles/me/username` is called with `{"username": "johndoe"}`
- **THEN** the response is `204 No Content` and the username is updated

#### Scenario: Username conflict
- **WHEN** `PATCH /api/v1/profiles/me/username` is called with a username already taken
- **THEN** the response is `409 Conflict`

## MODIFIED Requirements

### Requirement: Profile aggregate root
The `Profile` class SHALL extend `AggregateRoot[ProfileId]` and be located at `core/domain/profile/entity.py`. It SHALL hold: `id_: ProfileId`, `account_id: AccountId` (from shared kernel), `username: Username | None`, `first_name: FirstName | None`, `last_name: LastName | None`, `birth_date: BirthDate | None`.

#### Scenario: Create empty profile
- **WHEN** `Profile.create(id_, account_id)` is called without optional fields
- **THEN** profile is created with `username=None`, `first_name=None`, `last_name=None`, `birth_date=None` and a `ProfileCreated` event is registered

#### Scenario: Create profile with username
- **WHEN** `Profile.create(id_, account_id, username=Username("johndoe"))` is called
- **THEN** profile is created with the given username and `first_name=None`, `last_name=None`, `birth_date=None`, and a `ProfileCreated` event is registered

### Requirement: Profile domain events
Profile events SHALL be located at `core/domain/profile/events.py`: `ProfileCreated(profile_id, account_id, username)`, `UsernameChanged(profile_id, old_username, new_username)`, `ProfileUpdated(profile_id, old_first_name, new_first_name, old_last_name, new_last_name, old_birth_date, new_birth_date, old_username, new_username)`.

#### Scenario: ProfileCreated event fields
- **WHEN** a Profile is created
- **THEN** the `ProfileCreated` event contains `profile_id`, `account_id`, and `username` (may be None)

#### Scenario: ProfileUpdated event on full update
- **WHEN** `profile.update(...)` results in at least one field change
- **THEN** a `ProfileUpdated` event is registered with before/after values for all mutable fields

## REMOVED Requirements

### Requirement: API endpoint PUT /api/v1/profiles/me/username
**Reason**: Replaced by the more ergonomic `PUT /api/v1/profiles/me` (full update) and `PATCH /api/v1/profiles/me/username` (username-only partial update).
**Migration**: API clients using `PUT /api/v1/profiles/me/username` MUST switch to `PATCH /api/v1/profiles/me/username` with the same request body.
