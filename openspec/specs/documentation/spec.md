## Requirements

### Requirement: README reflects current JWT authentication architecture
The README.md SHALL accurately describe the current JWT access token + refresh token authentication system, removing all references to the removed AuthSession domain aggregate and cookie-based sessions.

#### Scenario: AuthSession references removed
- **WHEN** a reader reviews the README domain layer documentation
- **THEN** there SHALL be no references to AuthSession as a domain aggregate, auth session events, or session-based authentication

#### Scenario: JWT authentication documented
- **WHEN** a reader reviews the README authentication documentation
- **THEN** the README SHALL describe JWT access tokens (short-lived, stateless) and refresh tokens (long-lived, server-side stored) as the authentication mechanism

#### Scenario: API endpoints accurate
- **WHEN** a reader reviews the README API section
- **THEN** the documented endpoints SHALL match the current API under `/api/v1/accounts/` and `/api/v1/profiles/`, with no references to the old `/api/v1/users/` or `/api/v1/account/` routes

#### Scenario: Project structure tree accurate
- **WHEN** a reader reviews the README project structure
- **THEN** the file tree SHALL reflect the bounded-context-first layout with `src/account/`, `src/core/`, and `src/shared/` top-level directories, each containing `domain/`, `application/`, and `infrastructure/` subdirectories

#### Scenario: Code examples match implementation
- **WHEN** a reader reviews inline code examples
- **THEN** the examples SHALL use `Account` and `Profile` aggregate names, `AccountId`, `Email`, `AccountRole`, `AccountCreated`, `ProfileCreated`, `AccountRepository`, `ProfileRepository`, and other current naming

#### Scenario: Configuration section includes JWT settings
- **WHEN** a reader reviews the configuration section
- **THEN** the README SHALL mention JWT-related configuration (`JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRY_MIN`, `REFRESH_TOKEN_EXPIRY_DAYS`, `JWT_SECRET`)

### Requirement: README documents bounded-context-first architecture
The README.md SHALL describe the project as organized into bounded contexts (`account/`, `core/`, `shared/`) with each context containing its own `domain/`, `application/`, and `infrastructure/` layers.

#### Scenario: Bounded context overview
- **WHEN** a reader reviews the architecture overview
- **THEN** the README SHALL explain that the codebase is organized by bounded context first, with layers inside each context

#### Scenario: Account bounded context documented
- **WHEN** a reader looks for Account domain documentation
- **THEN** the README SHALL describe the Account aggregate (entity, value objects, events, repository) located in `src/account/domain/account/`

#### Scenario: Profile bounded context documented
- **WHEN** a reader looks for Profile domain documentation
- **THEN** the README SHALL describe the Profile aggregate (entity, value objects, events, repository) located in `src/core/domain/profile/`

#### Scenario: Shared kernel documented
- **WHEN** a reader looks for shared infrastructure documentation
- **THEN** the README SHALL describe `src/shared/` as containing base classes, shared value objects (`AccountId`), DI configuration, and cross-cutting infrastructure

### Requirement: README documents cross-context integration via domain events
The README.md SHALL describe how bounded contexts communicate through domain events rather than direct imports.

#### Scenario: Account-to-Profile event flow documented
- **WHEN** a reader reviews the cross-context integration section
- **THEN** the README SHALL explain that when an Account is created, an `AccountCreated` event is emitted, and the Core BC handles it via `CreateProfileOnAccountCreated` to create a Profile

#### Scenario: No direct cross-context domain imports
- **WHEN** a reader reviews the architecture constraints
- **THEN** the README SHALL state that bounded contexts do not import from each other's domain layers directly

### Requirement: README documents Account and Profile as separate aggregates
The README.md SHALL document Account and Profile as two distinct aggregate roots in separate bounded contexts, replacing all references to the old single `User` aggregate.

#### Scenario: Account aggregate documented
- **WHEN** a reader reviews the aggregate documentation
- **THEN** the README SHALL show Account as an aggregate root with `AccountId`, `Email`, `AccountPasswordHash`, `AccountRole`, and `is_active` fields

#### Scenario: Profile aggregate documented
- **WHEN** a reader reviews the aggregate documentation
- **THEN** the README SHALL show Profile as an aggregate root with `ProfileId`, `AccountId` (reference), and optional `Username`

#### Scenario: No User aggregate references
- **WHEN** a reader searches the README for "User aggregate" or `domain/user/`
- **THEN** there SHALL be no such references

### Requirement: Outdated doc images removed
The README.md SHALL NOT reference doc images that depict outdated API routes or architecture.

#### Scenario: handlers.png removed
- **WHEN** a reader reviews the README
- **THEN** there SHALL be no reference to `docs/handlers.png`, and the file SHALL be deleted from the repository

#### Scenario: Conceptual SVGs retained
- **WHEN** a reader reviews the architecture diagrams
- **THEN** the generic architectural SVGs (onion diagrams, dependency graphs, config flow) SHALL still be present and referenced
