## MODIFIED Requirements

### Requirement: Use-case-per-directory structure under application/
The system SHALL organize each use case as a directory under its bounded context's `application/` directory containing: `command.py` (or `query.py`), `handler.py`, and `port.py`. Use case directories MUST use snake_case naming matching the operation.

Account BC use cases SHALL be under `account/application/`.
Core BC use cases SHALL be under `core/application/`.

#### Scenario: Each use case has command, handler, and port
- **WHEN** inspecting any use case directory under `src/account/application/` or `src/core/application/`
- **THEN** it contains at minimum a handler module and a port module

### Requirement: Command/Query DTOs are plain dataclasses
Each use case MUST define a command or query DTO (e.g., `CreateAccountCommand`, `ListAccountsQuery`) as a frozen dataclass. Commands represent write intent; queries represent read intent. DTOs MUST NOT contain domain objects — only primitives and simple types.

#### Scenario: Command DTO contains only primitives
- **WHEN** inspecting a command dataclass (e.g., `CreateAccountCommand`)
- **THEN** its fields are primitive types (str, int, bool, UUID) — not domain entities or value objects

### Requirement: Handler implements the use case orchestration
Each handler MUST accept its command/query DTO and return a result. Handlers orchestrate domain logic by: (1) loading aggregates from repositories, (2) calling domain methods, (3) persisting changes via unit of work, (4) dispatching domain events. Handlers MUST NOT contain business rules — those belong in domain services or aggregate methods. Handlers MUST depend on application-layer ports for infrastructure operations (e.g., `TokenPairIssuer` for token issuance), not on concrete infrastructure services.

#### Scenario: Handler orchestrates domain objects
- **WHEN** `CreateAccountHandler.execute(command)` is called
- **THEN** it uses the `AccountRepository` port to persist and the `AccountUnitOfWork` to commit — it does NOT implement business validation itself

#### Scenario: LogInHandler depends on TokenPairIssuer port
- **WHEN** inspecting `LogInHandler.__init__`
- **THEN** it accepts a `TokenPairIssuer` parameter, not a concrete `RefreshTokenService`

#### Scenario: RefreshTokenHandler depends on TokenPairRefresher port
- **WHEN** inspecting `RefreshTokenHandler.__init__`
- **THEN** it accepts a `TokenPairRefresher` parameter, not a concrete `RefreshTokenService`

### Requirement: Port defines the driver interface
Each use case MUST define a `port.py` with a protocol/ABC that the handler implements. Infrastructure (REST controllers) depend on this port, not on the handler directly.

#### Scenario: REST controller depends on port, not handler
- **WHEN** a REST controller needs the create-account use case
- **THEN** it depends on `CreateAccountUseCase` (the port), which is satisfied by `CreateAccountHandler` via DI

### Requirement: Unit of Work port per bounded context
Each bounded context SHALL define its own `UnitOfWork` protocol in its `application/shared/` directory. `AccountUnitOfWork` in `account/application/shared/account_unit_of_work.py` and `CoreUnitOfWork` in `core/application/shared/core_unit_of_work.py`. Each abstracts transaction commit/rollback for its context. Handlers MUST use their context's UoW rather than directly managing database sessions.

#### Scenario: AccountUnitOfWork is framework-agnostic
- **WHEN** inspecting `account/application/shared/account_unit_of_work.py`
- **THEN** it defines a protocol with `commit()` and `rollback()` methods and imports no infrastructure libraries

#### Scenario: CoreUnitOfWork is framework-agnostic
- **WHEN** inspecting `core/application/shared/core_unit_of_work.py`
- **THEN** it defines a protocol with `commit()` and `rollback()` methods and imports no infrastructure libraries

### Requirement: Application use cases cover all operations
The system SHALL provide use case directories for all operations organized by bounded context:

**Account BC** (`account/application/`): `sign_up`, `log_in`, `change_password`, `create_account`, `current_account`, `list_accounts`, `activate_account`, `deactivate_account`, `set_account_password`, `grant_admin`, `revoke_admin`, `refresh_token`.

**Core BC** (`core/application/`): `get_my_profile`, `set_username`, `list_profiles`.

#### Scenario: All Account BC endpoints have corresponding use cases
- **WHEN** listing directories under `src/account/application/`
- **THEN** there is one directory per account operation including `refresh_token`

#### Scenario: All Core BC endpoints have corresponding use cases
- **WHEN** listing directories under `src/core/application/`
- **THEN** there are directories for `get_my_profile`, `set_username`, and `list_profiles`

### Requirement: LogInHandler uses email instead of username
The `LogInHandler` MUST accept a `LogInCommand` with `email` and `password` fields (not `username`). It SHALL look up the account via `AccountRepository.get_by_email()`.

#### Scenario: Login by email
- **WHEN** `LogInHandler.execute(LogInCommand(email="user@example.com", password="pass"))` is called
- **THEN** it looks up the account by email, validates password, and returns a token pair

### Requirement: SignUpHandler uses email instead of username
The `SignUpHandler` MUST accept a `SignUpCommand` with `email` and `password` fields (not `username`). It SHALL create an Account with the given email.

#### Scenario: Signup with email
- **WHEN** `SignUpHandler.execute(SignUpCommand(email="user@example.com", password="pass"))` is called
- **THEN** an Account is created with the email, and the handler returns `SignUpResponse(id=account_id)`

### Requirement: CurrentAccountHandler replaces CurrentUserHandler
The `CurrentAccountHandler` SHALL load the current account by ID from `IdentityProvider` and return account data. If the account is not found or inactive, it SHALL revoke access and raise an error.

#### Scenario: Current account returns account data
- **WHEN** `CurrentAccountHandler.execute()` is called with a valid token
- **THEN** it returns the account's id, email, role, and is_active status

## ADDED Requirements

### Requirement: GetMyProfileHandler use case
The `GetMyProfileHandler` in `core/application/get_my_profile/` SHALL load the current account ID from `IdentityProvider`, look up the profile by account ID via `ProfileRepository`, and return the profile data.

#### Scenario: Get own profile
- **WHEN** `GetMyProfileHandler.execute()` is called
- **THEN** it returns the profile's id, account_id, and username (may be None)

#### Scenario: Profile not found
- **WHEN** no profile exists for the current account
- **THEN** `ProfileNotFoundByAccountIdError` is raised

### Requirement: SetUsernameHandler use case
The `SetUsernameHandler` in `core/application/set_username/` SHALL load the current account ID from `IdentityProvider`, look up the profile, call `profile.set_username(username)`, persist via `CoreUnitOfWork`, and dispatch events.

#### Scenario: Set username
- **WHEN** `SetUsernameHandler.execute(SetUsernameCommand(username="johndoe"))` is called
- **THEN** the profile's username is updated and changes are committed

#### Scenario: Username already taken
- **WHEN** the username is already in use by another profile
- **THEN** `UsernameAlreadyExistsError` is raised

### Requirement: ListProfilesHandler use case
The `ListProfilesHandler` in `core/application/list_profiles/` SHALL return a paginated list of profiles. It SHALL require the caller to have appropriate permissions (admin or above).

#### Scenario: List profiles with pagination
- **WHEN** `ListProfilesHandler.execute(ListProfilesQuery(limit=20, offset=0))` is called by an admin
- **THEN** it returns a `ListProfilesQM` with profiles list and total count

## REMOVED Requirements

### Requirement: Application use cases cover all operations
**Reason**: Replaced by the bounded-context-aware version above that organizes use cases under `account/application/` and `core/application/` instead of a flat `application/` directory.
**Migration**: Use cases move to their respective bounded context directories with renamed commands and handlers.
