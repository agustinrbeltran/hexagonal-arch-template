## ADDED Requirements

### Requirement: Profile aggregate root
The `Profile` class SHALL extend `AggregateRoot[ProfileId]` and be located at `core/domain/profile/entity.py`. It SHALL hold: `id_: ProfileId`, `account_id: AccountId` (from shared kernel), `username: Username | None`.

#### Scenario: Create empty profile
- **WHEN** `Profile.create(id_, account_id)` is called without username
- **THEN** profile is created with `username=None` and a `ProfileCreated` event is registered

#### Scenario: Create profile with username
- **WHEN** `Profile.create(id_, account_id, username=Username("johndoe"))` is called
- **THEN** profile is created with the given username and a `ProfileCreated` event is registered

### Requirement: ProfileId value object
The `ProfileId` value object SHALL be located at `core/domain/profile/value_objects.py`. It SHALL wrap a UUID.

#### Scenario: Construct ProfileId
- **WHEN** `ProfileId(uuid_value)` is constructed
- **THEN** the value object is created with the UUID value

### Requirement: Username value object
The `Username` value object SHALL be located at `core/domain/profile/value_objects.py`. It SHALL enforce: 5-20 characters, must start and end with letter or digit, can contain letters, digits, `.`, `-`, `_`, no consecutive special characters.

#### Scenario: Valid username
- **WHEN** `Username("john.doe")` is constructed
- **THEN** the value object is created successfully

#### Scenario: Username too short
- **WHEN** `Username("ab")` is constructed
- **THEN** a `DomainTypeError` is raised

### Requirement: Profile username change
The Profile aggregate SHALL support `set_username(username: Username)` which updates the username and registers a `UsernameChanged` event. This operation SHALL be idempotent.

#### Scenario: Set username for the first time
- **WHEN** `set_username(Username("johndoe"))` is called on a profile with `username=None`
- **THEN** username is set and `UsernameChanged` event is registered

#### Scenario: Change existing username
- **WHEN** `set_username(Username("newname"))` is called on a profile with existing username
- **THEN** username is updated and `UsernameChanged` event is registered

#### Scenario: Set same username
- **WHEN** `set_username(Username("same"))` is called on a profile already with username "same"
- **THEN** no event is registered (idempotent)

### Requirement: Profile domain events
Profile events SHALL be located at `core/domain/profile/events.py`: `ProfileCreated(profile_id, account_id, username)`, `UsernameChanged(profile_id, old_username, new_username)`, `ProfileUpdated(profile_id, old/new fields for first_name, last_name, birth_date, username)`, `ProfilePatchApplied(profile_id, first_name, last_name, birth_date, username)` where each field in `ProfilePatchApplied` is a `tuple[old, new] | None` delta.

#### Scenario: ProfileCreated event fields
- **WHEN** a Profile is created
- **THEN** the `ProfileCreated` event contains `profile_id`, `account_id`, and `username` (may be None)

#### Scenario: ProfilePatchApplied event fields
- **WHEN** `profile.apply_patch()` changes one or more fields
- **THEN** the `ProfilePatchApplied` event contains `profile_id` and delta tuples only for the fields that changed; unchanged fields are `None`

### Requirement: ProfileRepository protocol
The `ProfileRepository` protocol SHALL be located at `core/domain/profile/repository.py`. It SHALL define: `save(profile)`, `get_by_id(profile_id, for_update=False)`, `get_by_account_id(account_id, for_update=False)`, `get_all(pagination, sorting)`. The `save(profile)` method SHALL have upsert semantics: it MUST persist the profile regardless of whether the profile already exists in the database (INSERT for new profiles, UPDATE for existing profiles).

#### Scenario: Get profile by account ID
- **WHEN** `get_by_account_id(account_id)` is called
- **THEN** returns the Profile if found, None otherwise

#### Scenario: Get all profiles with pagination
- **WHEN** `get_all(pagination, sorting)` is called
- **THEN** returns `ListProfilesQM` with `profiles` list and `total` count

#### Scenario: Save new profile inserts row
- **WHEN** `save(profile)` is called with a Profile that does not yet exist in the database
- **THEN** a new row is inserted into the profiles table

#### Scenario: Save existing profile updates row
- **WHEN** `save(profile)` is called with a Profile whose ID already exists in the database
- **THEN** the existing row is updated to reflect the current entity state

### Requirement: set_username use case persists the updated profile
The `SetUsernameHandler` SHALL call `profile_repository.save(profile)` after calling `profile.set_username(username)` and before calling `event_dispatcher.dispatch()`. This ensures the username change is flushed and committed atomically with the outbox entry.

#### Scenario: Username is persisted after set_username
- **GIVEN** an existing profile with no username
- **WHEN** `SetUsernameHandler.execute(SetUsernameCommand(username="johndoe"))` is called
- **THEN** the profile row in the database has `username = "johndoe"`

#### Scenario: Outbox entry and username change are atomic
- **GIVEN** `SetUsernameHandler` calls `save()`, then `dispatch()`, then `commit()`
- **WHEN** the unit of work commits
- **THEN** both the updated profile row and the `UsernameChanged` outbox entry are committed in the same transaction

### Requirement: Profile domain errors
Profile-specific errors SHALL be located at `core/domain/profile/errors.py`: `ProfileNotFoundByIdError`, `ProfileNotFoundByAccountIdError`, `UsernameAlreadyExistsError`.

#### Scenario: Profile not found by account ID
- **WHEN** `ProfileNotFoundByAccountIdError(account_id)` is raised
- **THEN** the error contains the account ID that was not found

### Requirement: ProfileIdGenerator port
The `ProfileIdGenerator` port SHALL be located at `core/domain/profile/ports.py` and provide a `generate()` method returning `ProfileId`.

#### Scenario: Generate profile ID
- **WHEN** `ProfileIdGenerator.generate()` is called
- **THEN** a new unique `ProfileId` is returned

### Requirement: Profile apply_patch method
The `Profile` aggregate SHALL expose `apply_patch(*, first_name, last_name, birth_date, username)` at `core/domain/profile/entity.py`. Each parameter SHALL accept `<ValueObject> | None | _Unset` with a default of `UNSET`. The method SHALL skip any field that is `UNSET`, update only the fields that differ from current state, and register a `ProfilePatchApplied` event if at least one field changed. It SHALL return `True` if any field was mutated, `False` otherwise.

#### Scenario: Partial patch mutates only provided fields
- **WHEN** `profile.apply_patch(first_name=FirstName("Andres"))` is called on a profile with `last_name="Smith"`, `birth_date=date(1990,1,1)`
- **THEN** `profile.first_name == FirstName("Andres")`, `profile.last_name` and `profile.birth_date` are unchanged, and one `ProfilePatchApplied` event is registered

#### Scenario: UNSET fields are completely ignored
- **WHEN** `profile.apply_patch(username=UNSET)` is called (all fields UNSET)
- **THEN** no field is mutated and no event is registered

#### Scenario: Explicit None clears the field
- **WHEN** `profile.apply_patch(birth_date=None)` is called on a profile with `birth_date=date(1990,1,1)`
- **THEN** `profile.birth_date is None` and a `ProfilePatchApplied` event is registered with `birth_date=("1990-01-01", None)`

#### Scenario: No-op patch returns False
- **WHEN** `profile.apply_patch(first_name=FirstName("Andres"))` is called on a profile already having `first_name=FirstName("Andres")`
- **THEN** the method returns `False` and no event is registered

### Requirement: ProfilePatchApplied domain event carries delta only
The `ProfilePatchApplied` event SHALL be located at `core/domain/profile/events.py`. It SHALL contain `profile_id: UUID` and one optional delta field per mutable attribute: `first_name: tuple[str | None, str | None] | None`, `last_name: tuple[str | None, str | None] | None`, `birth_date: tuple[date | None, date | None] | None`, `username: tuple[str | None, str | None] | None`. Each delta field is `(old_value, new_value)` when that field changed, or `None` when it was not touched.

#### Scenario: Delta contains only changed fields
- **WHEN** `profile.apply_patch(first_name=FirstName("Andres"))` is called
- **THEN** the `ProfilePatchApplied` event has `first_name=("old", "Andres")` and `last_name=None`, `birth_date=None`, `username=None`

#### Scenario: Full patch produces full delta
- **WHEN** `profile.apply_patch(first_name=FirstName("A"), last_name=LastName("B"), birth_date=BirthDate(date(2000,1,1)), username=Username("ab_cd"))` is called and all fields differ
- **THEN** all four delta fields in `ProfilePatchApplied` are non-None tuples
