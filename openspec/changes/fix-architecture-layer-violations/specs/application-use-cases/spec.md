## MODIFIED Requirements

### Requirement: Handler implements the use case orchestration
Each handler MUST accept its command/query DTO and return a result. Handlers orchestrate domain logic by: (1) loading aggregates from repositories, (2) calling domain methods, (3) persisting changes via unit of work, (4) dispatching domain events. Handlers MUST NOT contain business rules — those belong in domain services or aggregate methods. Handlers MUST depend on application-layer ports (ABCs/Protocols) for all collaborating use cases and infrastructure operations. Specifically, when a handler depends on another use case, it SHALL type-hint the port (e.g., `CurrentAccountUseCase`), NOT the concrete handler (e.g., `CurrentAccountHandler`).

#### Scenario: Handler orchestrates domain objects
- **WHEN** `CreateAccountHandler.execute(command)` is called
- **THEN** it uses the `AccountRepository` port to persist and the `AccountUnitOfWork` to commit — it does NOT implement business validation itself

#### Scenario: LogInHandler depends on TokenPairIssuer port
- **WHEN** inspecting `LogInHandler.__init__`
- **THEN** it accepts a `TokenPairIssuer` parameter, not a concrete `RefreshTokenService`

#### Scenario: RefreshTokenHandler depends on TokenPairRefresher port
- **WHEN** inspecting `RefreshTokenHandler.__init__`
- **THEN** it accepts a `TokenPairRefresher` parameter, not a concrete `RefreshTokenService`

#### Scenario: Handlers depend on CurrentAccountUseCase port, not CurrentAccountHandler
- **WHEN** inspecting `__init__` of any handler that needs the current account (SignUpHandler, CreateAccountHandler, ActivateAccountHandler, DeactivateAccountHandler, GrantAdminHandler, RevokeAdminHandler, ListAccountsHandler, SetAccountPasswordHandler, ChangePasswordHandler)
- **THEN** the parameter is typed as `CurrentAccountUseCase` (imported from `account.application.current_account.port`), NOT as `CurrentAccountHandler`

#### Scenario: DI container does not expose concrete handler as direct dependency
- **WHEN** inspecting the DI container configuration
- **THEN** there is no `provide_all(CurrentAccountHandler)` binding — handlers receive `CurrentAccountUseCase` via the standard port-based `provide(CurrentAccountHandler, provides=CurrentAccountUseCase)` binding

### Requirement: ListProfilesHandler uses AuthorizationGuard
The `ListProfilesHandler` SHALL depend on `AuthorizationGuard` (from `shared.domain.ports.authorization_guard`) for admin authorization checks instead of importing `AccountRole` and `AccountRepository` from the Account bounded context. It SHALL call `authorization_guard.require_admin()` before listing profiles.

#### Scenario: ListProfilesHandler has no Account domain imports
- **WHEN** inspecting `core/application/list_profiles/handler.py` imports
- **THEN** there are no imports from `account.domain`

#### Scenario: ListProfilesHandler delegates authorization to guard
- **WHEN** `ListProfilesHandler.execute(query)` is called
- **THEN** it calls `self._authorization_guard.require_admin()` before querying profiles
