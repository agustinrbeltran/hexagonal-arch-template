## ADDED Requirements

### Requirement: PatchProfileUseCase applies partial updates
The `PatchProfileUseCase` SHALL be located at `core/application/patch_profile/port.py`. Its `PatchProfileHandler` SHALL load the current account's profile, call `profile.apply_patch()` with only the fields explicitly provided in the command (non-UNSET values), persist via `CoreUnitOfWork`, and dispatch events.

#### Scenario: Only provided fields are mutated
- **WHEN** `PatchProfileHandler.execute(PatchProfileCommand(first_name="Andres"))` is called on a profile with existing `last_name`, `birth_date`, and `username`
- **THEN** only `first_name` is updated; `last_name`, `birth_date`, and `username` retain their existing values

#### Scenario: Explicitly null field is cleared
- **WHEN** `PatchProfileHandler.execute(PatchProfileCommand(birth_date=None))` is called (with `birth_date` explicitly set, not UNSET)
- **THEN** the profile's `birth_date` is set to `NULL` in the database

#### Scenario: Profile not found raises error
- **WHEN** no profile exists for the current account
- **THEN** `ProfileNotFoundByAccountIdError` is raised

#### Scenario: No-op patch produces no event
- **WHEN** all provided fields already match the current profile values
- **THEN** `ProfilePatchApplied` is NOT registered and no outbox entry is created

### Requirement: PatchProfileCommand uses UNSET sentinel
The `PatchProfileCommand` SHALL be a frozen dataclass located at `core/application/patch_profile/command.py`. Each field (`first_name`, `last_name`, `birth_date`, `username`) SHALL default to `UNSET` (from `shared.domain.unset`). The handler SHALL pass only non-UNSET fields to `profile.apply_patch()`.

#### Scenario: Command with single field
- **WHEN** `PatchProfileCommand(first_name="Andres")` is constructed
- **THEN** `first_name == "Andres"` and all other fields are `UNSET`

#### Scenario: Command with explicit null
- **WHEN** `PatchProfileCommand(birth_date=None)` is constructed
- **THEN** `birth_date is None` (not UNSET) and all other fields are `UNSET`

### Requirement: PATCH HTTP endpoint delegates to PatchProfileUseCase
The `PATCH /profiles/me` route SHALL inject `PatchProfileUseCase` (not `UpdateProfileUseCase`). It SHALL build a `PatchProfileCommand` using only the fields present in the request body (`model_fields_set`), leaving all absent fields as `UNSET`.

#### Scenario: PATCH with partial body
- **WHEN** `PATCH /profiles/me` is called with `{"first_name": "Andres"}`
- **THEN** a `PatchProfileCommand(first_name="Andres")` is executed and the response is `204 No Content`

#### Scenario: PATCH with empty body
- **WHEN** `PATCH /profiles/me` is called with `{}`
- **THEN** the handler executes with all fields UNSET, no mutation occurs, response is `204 No Content`
