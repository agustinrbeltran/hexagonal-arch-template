## ADDED Requirements

### Requirement: Persistence adapters under infrastructure/persistence/
The system SHALL place all SQLAlchemy repository implementations and table mappers under `infrastructure/persistence/`. This includes `SqlaUserRepository`, `SqlaAuthSessionGateway`, imperative table mappings, and session factories.

#### Scenario: SQLAlchemy repository implements domain port
- **WHEN** `SqlaUserRepository` is defined in `infrastructure/persistence/`
- **THEN** it implements the `UserRepository` protocol from `domain/user/repository.py`

#### Scenario: Imperative table mappings live in persistence
- **WHEN** inspecting `infrastructure/persistence/mappers/`
- **THEN** it contains the SQLAlchemy `Table` definitions and `map_imperatively()` calls for User and AuthSession

### Requirement: HTTP driver adapters under infrastructure/http/
The system SHALL place all FastAPI controllers, routers, request/response DTOs, middleware, and error handlers under `infrastructure/http/`. Controllers are driver adapters that convert HTTP requests into application-layer port calls.

#### Scenario: REST controller calls application port
- **WHEN** the create-user REST controller handles a POST request
- **THEN** it converts the request body into a `CreateUserCommand`, calls the `CreateUserUseCase` port, and returns an HTTP response

#### Scenario: Controllers do not import domain layer directly
- **WHEN** inspecting imports in `infrastructure/http/controllers/`
- **THEN** controllers import application ports (use case interfaces) — not domain entities or repositories

### Requirement: Security adapters under infrastructure/security/
The system SHALL place bcrypt password hashing, JWT token processing, and cookie-based session transport under `infrastructure/security/`.

#### Scenario: Password hasher implements domain port
- **WHEN** `BcryptPasswordHasher` is defined in `infrastructure/security/`
- **THEN** it implements the `PasswordHasher` protocol defined in the domain or application layer

### Requirement: DI composition root under infrastructure/config/di/
The system SHALL place all Dishka provider modules under `infrastructure/config/di/`. Provider modules MUST be organized by layer: `domain.py`, `application.py`, `infrastructure.py`, `settings.py`.

#### Scenario: DI providers wire ports to adapters
- **WHEN** the Dishka container is initialized
- **THEN** each domain port (e.g., `UserRepository`) is bound to its infrastructure adapter (e.g., `SqlaUserRepository`)

#### Scenario: Composition root is the only place that knows all concrete types
- **WHEN** inspecting `infrastructure/config/di/`
- **THEN** it is the only module that imports both domain ports AND infrastructure adapters

### Requirement: App factory under infrastructure/config/
The system SHALL place the FastAPI app factory (`create_web_app`, `create_ioc_container`) and settings models under `infrastructure/config/`.

#### Scenario: App factory bootstraps the application
- **WHEN** `create_web_app()` is called
- **THEN** it configures FastAPI, registers routers from `infrastructure/http/`, sets up middleware, and attaches the DI container

### Requirement: HTTP API contracts are preserved
All existing HTTP endpoints MUST maintain their current URL paths, HTTP methods, request body schemas, and response body schemas. The refactor MUST NOT change any external API behavior.

#### Scenario: Existing endpoints remain unchanged
- **WHEN** comparing the API schema before and after the refactor
- **THEN** all endpoint paths, methods, request schemas, and response schemas are identical
