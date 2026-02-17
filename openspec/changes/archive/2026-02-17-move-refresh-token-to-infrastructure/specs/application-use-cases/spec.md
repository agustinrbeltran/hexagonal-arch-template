## MODIFIED Requirements

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
