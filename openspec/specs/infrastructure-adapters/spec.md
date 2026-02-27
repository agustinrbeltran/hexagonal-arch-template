## ADDED Requirements

### Requirement: Supabase adapter for AccountProvisioner
The system SHALL provide a `SupabaseAccountProvisioner` class in `account/infrastructure/security/` that implements the `AccountProvisioner` protocol. It SHALL use the Supabase admin API (`admin.create_user`) to create users in `auth.users`. It SHALL raise `EmailAlreadyExistsError` if the email is already registered.

#### Scenario: Register creates user in auth.users
- **WHEN** `register(email, password)` is called
- **THEN** a user is created in `auth.users` via Supabase admin API with `email_confirm=True`
- **AND** the returned `AccountId` wraps the UUID from `auth.users.id`

#### Scenario: Register raises on duplicate email
- **WHEN** `register(email, password)` is called with an existing email
- **THEN** `EmailAlreadyExistsError` is raised

### Requirement: Supabase adapter for TokenPairIssuer
The system SHALL provide a Supabase adapter that implements the `TokenPairIssuer` protocol. It SHALL call `sign_in_with_password(email, password)` on the Supabase client. It SHALL raise `AuthenticationError` if credentials are invalid. The `access_token_expiry_seconds` property SHALL return the configured value.

#### Scenario: Issue token pair authenticates and returns tokens
- **WHEN** `issue_token_pair(email, password)` is called with valid credentials
- **THEN** it calls Supabase `sign_in_with_password` and returns `(access_token, refresh_token)`

#### Scenario: Issue token pair raises on invalid credentials
- **WHEN** `issue_token_pair(email, password)` is called with wrong password
- **THEN** `AuthenticationError` is raised

### Requirement: Supabase adapter for TokenPairRefresher
The system SHALL provide a Supabase adapter that implements the `TokenPairRefresher` protocol. It SHALL call the Supabase refresh session endpoint.

#### Scenario: Refresh returns new token pair
- **WHEN** `refresh(refresh_token)` is called with a valid refresh token
- **THEN** it returns `(new_access_token, new_refresh_token)`

#### Scenario: Refresh raises on invalid token
- **WHEN** `refresh(refresh_token)` is called with an expired or invalid token
- **THEN** an appropriate error is raised

### Requirement: Supabase adapter for AccessRevoker
The system SHALL provide a Supabase adapter that implements the `AccessRevoker` protocol. It SHALL call the Supabase admin API to revoke all sessions for an account.

#### Scenario: Revoke all sessions for account
- **WHEN** `remove_all_account_access(account_id)` is called
- **THEN** all sessions for that account are revoked in Supabase

### Requirement: Supabase adapter for PasswordResetter
The system SHALL provide a Supabase adapter that implements the `PasswordResetter` protocol. It SHALL call the Supabase admin API (`admin.update_user_by_id`) to update the password.

#### Scenario: Reset password updates auth.users
- **WHEN** `reset_password(account_id, new_password)` is called
- **THEN** the user's password is updated in `auth.users` via admin API

### Requirement: AccountMetadata table mapper
The system SHALL provide an imperative SQLAlchemy mapper at `account/infrastructure/persistence/mappers/account.py` mapping `AccountMetadataRecord` to the `account_metadata` table. Columns: `account_id` (UUID, PK), `role` (accountrole enum), `is_active` (boolean). A read-only `auth_users_table` reference SHALL be defined for cross-schema joins.

#### Scenario: AccountMetadataRecord maps to account_metadata
- **WHEN** the mapper registry is initialized
- **THEN** `AccountMetadataRecord.account_id` maps to `account_metadata.account_id`, `AccountMetadataRecord.role` maps to `account_metadata.role`, `AccountMetadataRecord.is_active` maps to `account_metadata.is_active`

#### Scenario: Auth users table is defined for read-only joins
- **WHEN** inspecting the mapper module
- **THEN** an `auth_users_table` SQLAlchemy `Table` is defined with schema `"auth"` containing `id` and `email` columns

### Requirement: SqlaAccountRepository reads from cross-schema join
The `SqlaAccountRepository` SHALL reconstruct `Account` entities by joining `auth.users` (for `id`, `email`) with `account_metadata` (for `role`, `is_active`). The `save()` method SHALL only write to `account_metadata` using `session.merge()`.

#### Scenario: Get by email joins auth.users and account_metadata
- **WHEN** `get_by_email(email)` is called
- **THEN** it queries `auth.users JOIN account_metadata ON account_metadata.account_id = auth.users.id WHERE auth.users.email = ?`

#### Scenario: Get by id joins auth.users and account_metadata
- **WHEN** `get_by_id(account_id)` is called
- **THEN** it queries `auth.users JOIN account_metadata ON account_metadata.account_id = auth.users.id WHERE auth.users.id = ?`

#### Scenario: Save writes metadata only
- **WHEN** `save(account)` is called
- **THEN** it merges an `AccountMetadataRecord` with `account_id`, `role`, and `is_active` to `account_metadata`

### Requirement: JwtAccessTokenProcessor becomes verify-only
The `JwtAccessTokenProcessor` SHALL be renamed or refactored to remove the `encode()` method. It SHALL only decode and verify JWTs. The `jwt.decode()` call SHALL include `audience="authenticated"` validation.

#### Scenario: Decode validates audience
- **WHEN** `decode_account_id(token)` is called with a valid Supabase JWT
- **THEN** it verifies the `aud` claim equals `"authenticated"` and returns the `sub` (account_id)

#### Scenario: Decode rejects wrong audience
- **WHEN** `decode_account_id(token)` is called with a JWT where `aud != "authenticated"`
- **THEN** it returns None

### Requirement: Supabase client DI provider
The system SHALL provide a Dishka provider that creates a Supabase client instance at `Scope.APP` using `supabase_url` and `supabase_service_role_key` from settings. This client SHALL be injected into all Supabase adapters.

#### Scenario: Supabase client is app-scoped
- **WHEN** the DI container resolves the Supabase client
- **THEN** it returns a singleton instance created with the configured URL and service role key

### Requirement: Supabase settings
The `SecuritySettings` or a new `SupabaseSettings` model SHALL include `supabase_url: str` and `supabase_service_role_key: str`. Password-related settings (`pepper`, `hasher_work_factor`, `hasher_max_threads`, `hasher_semaphore_wait_timeout_s`) SHALL be removed.

#### Scenario: Supabase settings are loaded from config
- **WHEN** settings are loaded
- **THEN** `supabase_url` and `supabase_service_role_key` are available

#### Scenario: Password settings are removed
- **WHEN** inspecting `SecuritySettings`
- **THEN** no `PasswordSettings` or `password` field exists

## MODIFIED Requirements

### Requirement: Security adapters under account infrastructure
The system SHALL place Supabase auth adapters and JWT token verification under `account/infrastructure/security/`. The `IdentityProvider` implementation (`JwtBearerIdentityProvider`) remains in `shared/infrastructure/security/`. The `BcryptPasswordHasher` is removed. The `RefreshTokenService`, `RefreshTokenRepository`, `RefreshToken` dataclass, and `RefreshTokenIdGenerator` are removed.

#### Scenario: Supabase adapters implement application ports
- **WHEN** inspecting `account/infrastructure/security/`
- **THEN** it contains Supabase adapter(s) implementing `AccountProvisioner`, `TokenPairIssuer`, `TokenPairRefresher`, `AccessRevoker`, and `PasswordResetter`

#### Scenario: BcryptPasswordHasher is removed
- **WHEN** inspecting `account/infrastructure/security/`
- **THEN** no `BcryptPasswordHasher` or `PasswordHasher` implementation exists

#### Scenario: Identity provider in shared infrastructure
- **WHEN** `JwtBearerIdentityProvider` is defined in `shared/infrastructure/security/`
- **THEN** it implements the `IdentityProvider` protocol and verifies Supabase JWTs

### Requirement: DI composition root restructured
The DI composition root SHALL be updated to: remove `AccountService`, `PasswordHasher`, `AccountIdGenerator`, `HasherThreadPoolExecutor`, `HasherSemaphore` providers. Add providers for: Supabase client, `AccountProvisioner`, `PasswordResetter`. Update providers for: `TokenPairIssuer`, `TokenPairRefresher`, `AccessRevoker` to use Supabase adapters. Remove `AuthUnitOfWork`, `RefreshTokenRepository`, `RefreshTokenIdGenerator` providers.

#### Scenario: DI container provides AccountProvisioner
- **WHEN** the Dishka container resolves `AccountProvisioner`
- **THEN** it returns the Supabase adapter implementation

#### Scenario: DI container provides TokenPairIssuer
- **WHEN** the Dishka container resolves `TokenPairIssuer`
- **THEN** it returns the Supabase adapter implementation

#### Scenario: DI container does not provide AccountService
- **WHEN** inspecting the DI providers
- **THEN** no `AccountService` provider exists

### Requirement: Database migration for Supabase auth
The system SHALL provide a migration that:
1. Creates `public.account_metadata` table with `account_id` (UUID PK, FK to `auth.users(id)`), `role` (accountrole, NOT NULL, DEFAULT 'USER'), `is_active` (BOOLEAN, NOT NULL, DEFAULT TRUE)
2. Updates `profiles.account_id` FK to reference `auth.users(id)` instead of `accounts(id)`
3. Drops `public.refresh_tokens` table
4. Drops `public.accounts` table

#### Scenario: account_metadata table exists after migration
- **WHEN** the migration is applied
- **THEN** `public.account_metadata` exists with columns `account_id`, `role`, `is_active`
- **AND** `account_id` is a FK to `auth.users(id)`

#### Scenario: profiles FK updated
- **WHEN** the migration is applied
- **THEN** `profiles.account_id` references `auth.users(id)`

#### Scenario: accounts and refresh_tokens tables dropped
- **WHEN** the migration is applied
- **THEN** `public.accounts` and `public.refresh_tokens` do not exist

## REMOVED Requirements

### Requirement: Persistence adapters organized by bounded context
**Reason**: Partially superseded. The account persistence structure changes from mapping `AccountRecord` to `accounts` table to mapping `AccountMetadataRecord` to `account_metadata` table with cross-schema joins. Core BC persistence is unchanged.
**Migration**: Replace `AccountRecord` and accounts table mapper with `AccountMetadataRecord` and account_metadata table mapper. Update `AccountConverter`. Add `auth_users_table` read-only reference.

### Requirement: Accounts table mapper
**Reason**: The `accounts` table is replaced by `account_metadata`. The mapper changes entirely.
**Migration**: Replace with `AccountMetadataRecord` mapping to `account_metadata` table.

### Requirement: SqlaAccountUnitOfWork implementation
**Reason**: The constraint violation handling changes. The email uniqueness constraint is now in `auth.users` (handled by `AccountProvisioner`), not in `account_metadata`. The UoW only needs to handle `account_metadata` constraints (role, etc.).
**Migration**: Update `SqlaAccountUnitOfWork` to remove email-specific `IntegrityError` handling. Email uniqueness errors are raised by `AccountProvisioner`, not by the UoW commit.
