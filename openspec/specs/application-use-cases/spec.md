## ADDED Requirements

### Requirement: Use-case-per-directory structure under application/
The system SHALL organize each use case as a directory under `application/` containing: `command.py` (or `query.py`), `handler.py`, and `port.py`. Use case directories MUST use kebab-case naming matching the operation (e.g., `create_user/`, `sign_up/`, `log_in/`).

#### Scenario: Each use case has command, handler, and port
- **WHEN** inspecting any use case directory under `src/application/`
- **THEN** it contains at minimum a handler module and a port module

### Requirement: Command/Query DTOs are plain dataclasses
Each use case MUST define a command or query DTO (e.g., `CreateUserCommand`, `ListUsersQuery`) as a frozen dataclass. Commands represent write intent; queries represent read intent. DTOs MUST NOT contain domain objects — only primitives and simple types.

#### Scenario: Command DTO contains only primitives
- **WHEN** inspecting a command dataclass (e.g., `CreateUserCommand`)
- **THEN** its fields are primitive types (str, int, bool, UUID) — not domain entities or value objects

### Requirement: Handler implements the use case orchestration
Each handler MUST accept its command/query DTO and return a result. Handlers orchestrate domain logic by: (1) loading aggregates from repositories, (2) calling domain methods, (3) persisting changes via unit of work, (4) dispatching domain events. Handlers MUST NOT contain business rules — those belong in domain services or aggregate methods. Handlers MUST depend on application-layer ports for infrastructure operations (e.g., `TokenPairIssuer` for token issuance), not on concrete infrastructure services.

#### Scenario: Handler orchestrates domain objects
- **WHEN** `CreateUserHandler.execute(command)` is called
- **THEN** it uses the `UserRepository` port to persist and the `UnitOfWork` to commit — it does NOT implement business validation itself

#### Scenario: LogInHandler depends on TokenPairIssuer port
- **WHEN** inspecting `LogInHandler.__init__`
- **THEN** it accepts a `TokenPairIssuer` parameter, not a concrete `RefreshTokenService`

#### Scenario: RefreshTokenHandler depends on TokenPairRefresher port
- **WHEN** inspecting `RefreshTokenHandler.__init__`
- **THEN** it accepts a `TokenPairRefresher` parameter, not a concrete `RefreshTokenService`

#### Scenario: No application handler imports from domain/refresh_token/
- **WHEN** searching for imports from `domain.refresh_token` across `src/application/`
- **THEN** no such imports exist

### Requirement: Port defines the driver interface
Each use case MUST define a `port.py` with a protocol/ABC that the handler implements. Infrastructure (REST controllers) depend on this port, not on the handler directly.

#### Scenario: REST controller depends on port, not handler
- **WHEN** a REST controller needs the create-user use case
- **THEN** it depends on `CreateUserUseCase` (the port), which is satisfied by `CreateUserHandler` via DI

### Requirement: Unit of Work port in application/shared/
The system SHALL define a `UnitOfWork` protocol in `application/shared/unit_of_work.py` abstracting transaction commit/rollback. Handlers MUST use this port rather than directly managing database sessions.

#### Scenario: UnitOfWork port is framework-agnostic
- **WHEN** inspecting `application/shared/unit_of_work.py`
- **THEN** it defines a protocol with `commit()` and `rollback()` methods and imports no infrastructure libraries

### Requirement: Application use cases cover all operations
The system SHALL provide use case directories for all operations: `create_user`, `activate_user`, `deactivate_user`, `grant_admin`, `revoke_admin`, `set_user_password`, `list_users`, `current_user`, `sign_up`, `log_in`, `change_password`, `refresh_token`.

#### Scenario: All endpoints have corresponding use cases
- **WHEN** listing directories under `src/application/`
- **THEN** there is one directory per REST endpoint operation, including `refresh_token` and excluding `log_out`

### Requirement: LogInHandler returns a token pair
The `LogInHandler` MUST return a token pair (access token string + refresh token string) instead of returning `None`. It SHALL call the `TokenPairIssuer` port after credential validation. The handler MUST NOT check for "already authenticated" status — any valid credentials produce a new token pair.

#### Scenario: Login issues token pair
- **WHEN** `LogInHandler.execute(command)` succeeds
- **THEN** it returns an `(access_token, refresh_token)` tuple from `TokenPairIssuer.issue_token_pair()`

#### Scenario: Login does not check existing authentication
- **WHEN** `LogInHandler.execute(command)` is called
- **THEN** it does NOT call `CurrentUserHandler` or check for existing sessions

### Requirement: RefreshTokenHandler use case at application/refresh_token/
The system SHALL provide a `refresh_token` use case with `command.py` (containing `RefreshTokenCommand` with a `refresh_token: str` field), `handler.py` (containing `RefreshTokenHandler`), and `port.py` (containing `RefreshTokenUseCase` ABC). The handler MUST call the `TokenPairRefresher` port and return a new token pair.

#### Scenario: RefreshTokenHandler returns new token pair
- **WHEN** `RefreshTokenHandler.execute(command)` is called with a valid refresh token
- **THEN** it returns a new `(access_token, refresh_token)` tuple

#### Scenario: RefreshTokenHandler propagates errors
- **WHEN** `RefreshTokenHandler.execute(command)` is called with an invalid refresh token
- **THEN** it propagates `RefreshTokenNotFoundError` or `RefreshTokenExpiredError`
