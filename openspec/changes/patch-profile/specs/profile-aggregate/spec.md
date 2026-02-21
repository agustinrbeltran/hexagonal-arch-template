## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Profile domain events
Profile events SHALL be located at `core/domain/profile/events.py`: `ProfileCreated(profile_id, account_id, username)`, `UsernameChanged(profile_id, old_username, new_username)`, `ProfileUpdated(profile_id, old/new fields for first_name, last_name, birth_date, username)`, `ProfilePatchApplied(profile_id, first_name, last_name, birth_date, username)` where each field in `ProfilePatchApplied` is a `tuple[old, new] | None` delta.

#### Scenario: ProfileCreated event fields
- **WHEN** a Profile is created
- **THEN** the `ProfileCreated` event contains `profile_id`, `account_id`, and `username` (may be None)

#### Scenario: ProfilePatchApplied event fields
- **WHEN** `profile.apply_patch()` changes one or more fields
- **THEN** the `ProfilePatchApplied` event contains `profile_id` and delta tuples only for the fields that changed; unchanged fields are `None`
