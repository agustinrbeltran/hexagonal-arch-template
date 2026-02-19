## MODIFIED Requirements

### Requirement: Persistence adapters organized by bounded context
The system SHALL place SQLAlchemy repository implementations, table mappers, and converters under each bounded context's `infrastructure/persistence/` directory.

Account BC: `account/infrastructure/persistence/` with `SqlaAccountRepository`, account table mapper, `AccountRecord`, and `AccountConverter`.
Core BC: `core/infrastructure/persistence/` with `SqlaProfileRepository`, profile table mapper, `ProfileRecord`, and `ProfileConverter`.
Shared: Refresh token persistence stays under `account/infrastructure/` since it's Account BC infrastructure.

#### Scenario: SQLAlchemy repository implements domain port
- **WHEN** `SqlaAccountRepository` is defined in `account/infrastructure/persistence/`
- **THEN** it implements the `AccountRepository` protocol from `account/domain/account/repository.py`
- **AND** it queries `AccountRecord` and converts to `Account` via `AccountConverter`

#### Scenario: SqlaProfileRepository implements domain port
- **WHEN** `SqlaProfileRepository` is defined in `core/infrastructure/persistence/`
- **THEN** it implements the `ProfileRepository` protocol from `core/domain/profile/repository.py`
- **AND** it queries `ProfileRecord` and converts to `Profile` via `ProfileConverter`

#### Scenario: Repository save uses merge
- **WHEN** `save(entity)` is called on a repository
- **THEN** it converts the entity to a record via the converter and calls `session.merge(record)`

#### Scenario: Repository get converts record to entity
- **WHEN** `get_by_id(id)` is called on a repository
- **THEN** it queries for the record, and if found, converts it to a domain entity via the converter

#### Scenario: Imperative table mappings per context
- **WHEN** inspecting `account/infrastructure/persistence/mappers/`
- **THEN** it contains the SQLAlchemy `Table` definition for `accounts`, the `AccountRecord` dataclass, and `map_imperatively()` mapping `AccountRecord` to the table without `composite()`, `column_prefix`, or `exclude_properties`
- **WHEN** inspecting `core/infrastructure/persistence/mappers/`
- **THEN** it contains the SQLAlchemy `Table` definition for `profiles`, the `ProfileRecord` dataclass, and `map_imperatively()` mapping `ProfileRecord` to the table without `composite()`, `column_prefix`, or `exclude_properties`

### Requirement: HTTP driver adapters organized by bounded context
The system SHALL place FastAPI controllers and routers under each bounded context's `infrastructure/http/` directory.

Account BC: `account/infrastructure/http/` with controllers for all `/accounts/` endpoints.
Core BC: `core/infrastructure/http/` with controllers for all `/profiles/` endpoints.

#### Scenario: Account REST controller calls application port
- **WHEN** the create-account REST controller handles a POST request
- **THEN** it converts the request body into a `CreateAccountCommand`, calls the `CreateAccountUseCase` port, and returns an HTTP response

#### Scenario: Profile REST controller calls application port
- **WHEN** the set-username REST controller handles a PUT request
- **THEN** it converts the request body into a `SetUsernameCommand`, calls the `SetUsernameUseCase` port, and returns an HTTP response

### Requirement: Security adapters under account infrastructure
The system SHALL place bcrypt password hashing, JWT token processing, refresh token management, and access revocation under `account/infrastructure/security/`. The `IdentityProvider` implementation (`JwtBearerIdentityProvider`) SHALL move to `shared/infrastructure/security/` since it's used by both contexts.

#### Scenario: Password hasher implements domain port
- **WHEN** `BcryptPasswordHasher` is defined in `account/infrastructure/security/`
- **THEN** it implements the `PasswordHasher` protocol defined in Account domain

#### Scenario: Identity provider in shared infrastructure
- **WHEN** `JwtBearerIdentityProvider` is defined in `shared/infrastructure/security/`
- **THEN** it implements the `IdentityProvider` protocol from shared kernel and returns `AccountId`

### Requirement: JwtBearerIdentityProvider returns AccountId
The `JwtBearerIdentityProvider` SHALL extract the `sub` claim from the JWT and return it as an `AccountId` (from shared kernel) instead of `UserId`.

#### Scenario: Extracts account_id from Bearer token
- **WHEN** a request has `Authorization: Bearer <valid-jwt>` header
- **THEN** `get_current_account_id()` returns the `AccountId` from the JWT's `sub` claim

#### Scenario: Raises authentication error for missing header
- **WHEN** a request has no `Authorization` header
- **THEN** `get_current_account_id()` raises an authentication error

### Requirement: RefreshTokenAccessRevoker uses AccountId
The `RefreshTokenAccessRevoker` SHALL accept `AccountId` instead of `UserId` in its `remove_all_user_access()` method.

#### Scenario: Revokes all refresh tokens for an account
- **WHEN** `remove_all_account_access(account_id)` is called
- **THEN** all refresh tokens for that account are deleted from the database

### Requirement: Login controller uses email
The login controller SHALL accept `{email, password}` in the request body instead of `{username, password}`. The endpoint path SHALL be `POST /api/v1/accounts/login`.

#### Scenario: Login endpoint accepts email
- **WHEN** `POST /api/v1/accounts/login` is called with `{email, password}`
- **THEN** response is `200 OK` with JSON body `{access_token, refresh_token, token_type, expires_in}`

### Requirement: Signup controller uses email
The signup controller SHALL accept `{email, password}` in the request body instead of `{username, password}`. The endpoint path SHALL be `POST /api/v1/accounts/signup`.

#### Scenario: Signup endpoint accepts email
- **WHEN** `POST /api/v1/accounts/signup` is called with `{email, password}`
- **THEN** response is `201 Created` with `{id: account_uuid}`

### Requirement: Account router replaces user and account routers
A single `account_router` SHALL serve all `/api/v1/accounts/` endpoints, replacing both the old `account_router` and `user_router`. It SHALL include self-service endpoints (`/me`, `/signup`, `/login`, `/refresh`) and admin endpoints (`/`, `/{id}/...`).

#### Scenario: Unified accounts router
- **WHEN** the API route table is inspected
- **THEN** all account-related endpoints are under `/api/v1/accounts/`

### Requirement: Profile router for Core BC
A `profile_router` SHALL serve all `/api/v1/profiles/` endpoints.

#### Scenario: Profile endpoints registered
- **WHEN** the API route table is inspected
- **THEN** profile endpoints are under `/api/v1/profiles/`

### Requirement: DI composition root restructured
The DI composition root SHALL be organized with providers per bounded context: `AccountDomainProvider`, `AccountApplicationProvider`, `AccountInfrastructureProvider`, `CoreDomainProvider`, `CoreApplicationProvider`, `CoreInfrastructureProvider`, `SharedProvider`.

#### Scenario: DI container provides Account BC dependencies
- **WHEN** the Dishka container resolves `AccountRepository`
- **THEN** it returns a `SqlaAccountRepository` instance

#### Scenario: DI container provides Core BC dependencies
- **WHEN** the Dishka container resolves `ProfileRepository`
- **THEN** it returns a `SqlaProfileRepository` instance

### Requirement: Database migration for aggregate split
The system SHALL provide a migration that:
1. Renames `users` table to `accounts`
2. Renames `username` column to `email` and changes type to `VARCHAR(255)`
3. Renames `userrole` enum to `accountrole`
4. Creates `profiles` table with columns: `id` (UUID PK), `account_id` (UUID, NOT NULL, UNIQUE, FK to accounts.id), `username` (VARCHAR(20), UNIQUE, nullable)

#### Scenario: Accounts table exists after migration
- **WHEN** the migration is applied
- **THEN** the `accounts` table exists with columns `id`, `email`, `password_hash`, `role`, `is_active`

#### Scenario: Profiles table exists after migration
- **WHEN** the migration is applied
- **THEN** the `profiles` table exists with columns `id`, `account_id`, `username`

#### Scenario: Users table no longer exists
- **WHEN** the migration is applied
- **THEN** the `users` table does not exist

## ADDED Requirements

### Requirement: Accounts table mapper
The system SHALL provide an imperative SQLAlchemy mapper at `account/infrastructure/persistence/mappers/account.py` mapping `AccountRecord` to the `accounts` table. It SHALL NOT use `composite()` — all columns map directly to `AccountRecord` attributes with matching names.

#### Scenario: Account mapper uses direct column mapping
- **WHEN** the mapper registry is initialized
- **THEN** `AccountRecord.id` maps to `accounts.id`, `AccountRecord.email` maps to `accounts.email`, `AccountRecord.password_hash` maps to `accounts.password_hash`

### Requirement: Profiles table mapper
The system SHALL provide an imperative SQLAlchemy mapper at `core/infrastructure/persistence/mappers/profile.py` mapping `ProfileRecord` to the `profiles` table. It SHALL NOT use `composite()` — all columns map directly to `ProfileRecord` attributes with matching names.

#### Scenario: Profile mapper uses direct column mapping
- **WHEN** the mapper registry is initialized
- **THEN** `ProfileRecord.id` maps to `profiles.id`, `ProfileRecord.account_id` maps to `profiles.account_id`, `ProfileRecord.username` maps to `profiles.username`

### Requirement: SqlaAccountUnitOfWork implementation
The `SqlaAccountUnitOfWork` SHALL implement `AccountUnitOfWork` using the SQLAlchemy async session. It SHALL catch `IntegrityError` on commit and convert username uniqueness violations to `EmailAlreadyExistsError`.

#### Scenario: Email uniqueness violation
- **WHEN** `SqlaAccountUnitOfWork.commit()` encounters an IntegrityError on the email column
- **THEN** `EmailAlreadyExistsError` is raised

### Requirement: SqlaCoreUnitOfWork implementation
The `SqlaCoreUnitOfWork` SHALL implement `CoreUnitOfWork` using the SQLAlchemy async session. It SHALL catch `IntegrityError` on commit and convert username uniqueness violations to `UsernameAlreadyExistsError`.

#### Scenario: Username uniqueness violation
- **WHEN** `SqlaCoreUnitOfWork.commit()` encounters an IntegrityError on the username column
- **THEN** `UsernameAlreadyExistsError` is raised
