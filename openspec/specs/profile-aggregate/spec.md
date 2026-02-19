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
Profile events SHALL be located at `core/domain/profile/events.py`: `ProfileCreated(profile_id, account_id, username)`, `UsernameChanged(profile_id, old_username, new_username)`.

#### Scenario: ProfileCreated event fields
- **WHEN** a Profile is created
- **THEN** the `ProfileCreated` event contains `profile_id`, `account_id`, and `username` (may be None)

### Requirement: ProfileRepository protocol
The `ProfileRepository` protocol SHALL be located at `core/domain/profile/repository.py`. It SHALL define: `save(profile)`, `get_by_id(profile_id, for_update=False)`, `get_by_account_id(account_id, for_update=False)`, `get_all(pagination, sorting)`.

#### Scenario: Get profile by account ID
- **WHEN** `get_by_account_id(account_id)` is called
- **THEN** returns the Profile if found, None otherwise

#### Scenario: Get all profiles with pagination
- **WHEN** `get_all(pagination, sorting)` is called
- **THEN** returns `ListProfilesQM` with `profiles` list and `total` count

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
