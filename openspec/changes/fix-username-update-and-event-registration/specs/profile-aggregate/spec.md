## MODIFIED Requirements

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
