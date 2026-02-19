## 1. Database Migration

- [x] 1.1 Create Supabase migration: rename `users` table to `accounts`, rename `username` column to `email` (VARCHAR(255)), rename `userrole` enum to `accountrole`
- [x] 1.2 Create Supabase migration: create `profiles` table with `id` (UUID PK), `account_id` (UUID NOT NULL UNIQUE FK accounts.id), `username` (VARCHAR(20) UNIQUE nullable)
- [x] 1.3 Create Supabase migration: rename `refresh_tokens.user_id` column to `account_id`

## 2. Shared Kernel (`src/shared/`)

- [x] 2.1 Create `shared/` directory structure: `shared/domain/`, `shared/domain/ports/`, `shared/application/`, `shared/infrastructure/`, `shared/infrastructure/events/`, `shared/infrastructure/security/`
- [x] 2.2 Move domain base classes to `shared/domain/`: `entity.py`, `aggregate_root.py`, `value_object.py`, `domain_event.py`, `errors.py`
- [x] 2.3 Move pagination and sorting primitives to `shared/domain/`
- [x] 2.4 Create `shared/domain/account_id.py` with `AccountId` value object (UUID wrapper)
- [x] 2.5 Move `IdentityProvider` protocol to `shared/domain/ports/identity_provider.py`, rename method to `get_current_account_id() -> AccountId`
- [x] 2.6 Move permission base types (`Permission`, `AnyOf`, `PermissionContext`, `authorize`) to `shared/domain/authorization.py`
- [x] 2.7 Move `EventHandler` protocol to `shared/application/event_handler.py`
- [x] 2.8 Move `EventDispatcher` protocol to `shared/application/event_dispatcher.py`
- [x] 2.9 Move event registry (`@handles`, `get_handlers_for`, `auto_discover_handlers`) to `shared/infrastructure/events/registry.py`; update `auto_discover_handlers` to scan both `account.infrastructure.events.handlers` and `core.infrastructure.events.handlers`
- [x] 2.10 Move `InProcessEventDispatcher` to `shared/infrastructure/events/dispatcher.py`
- [x] 2.11 Move `JwtBearerIdentityProvider` to `shared/infrastructure/security/identity_provider.py`; update to return `AccountId`
- [x] 2.12 Add `__init__.py` files for all shared packages

## 3. Account Bounded Context - Domain Layer (`src/account/domain/`)

- [x] 3.1 Create `account/` directory structure: `account/domain/account/`, `account/application/`, `account/infrastructure/`
- [x] 3.2 Create `account/domain/account/enums.py` with `AccountRole` enum (rename from `UserRole`) and `SUBORDINATE_ROLES` mapping
- [x] 3.3 Create `account/domain/account/value_objects.py` with `Email` (new, validated), `AccountPasswordHash` (rename from `UserPasswordHash`), `RawPassword`
- [x] 3.4 Create `account/domain/account/events.py` with `AccountCreated`, `AccountActivated`, `AccountDeactivated`, `AccountRoleChanged`, `AccountPasswordChanged`
- [x] 3.5 Create `account/domain/account/errors.py` with `EmailAlreadyExistsError`, `AccountNotFoundByIdError`, `AccountNotFoundByEmailError`, `ActivationChangeNotPermittedError`, `RoleAssignmentNotPermittedError`, `RoleChangeNotPermittedError`
- [x] 3.6 Create `account/domain/account/ports.py` with `PasswordHasher`, `AccessRevoker`, `AccountIdGenerator`
- [x] 3.7 Create `account/domain/account/repository.py` with `AccountRepository` protocol (`save`, `get_by_id`, `get_by_email`, `get_all`) and `AccountQueryModel`, `ListAccountsQM`
- [x] 3.8 Create `account/domain/account/entity.py` with `Account` aggregate root (fields: id_, email, password_hash, role, is_active; methods: create, activate, deactivate, change_role, change_password)
- [x] 3.9 Create `account/domain/account/services.py` with `AccountService` (create, is_password_valid, change_password) and permission classes (`CanManageSelf`, `CanManageSubordinate`, `CanManageRole`, `AccountManagementContext`, `RoleManagementContext`)
- [x] 3.10 Add `__init__.py` files for all account domain packages

## 4. Account Bounded Context - Application Layer (`src/account/application/`)

- [x] 4.1 Create `account/application/shared/` with `account_unit_of_work.py` (AccountUnitOfWork protocol) and `auth_unit_of_work.py` (AuthUnitOfWork protocol)
- [x] 4.2 Create `account/application/shared/token_pair_issuer.py` and `token_pair_refresher.py` (move from old location, update UserId → AccountId)
- [x] 4.3 Migrate `sign_up` use case: rename command fields (username → email), use AccountService, AccountRepository, AccountUnitOfWork
- [x] 4.4 Migrate `log_in` use case: rename command fields (username → email), use `get_by_email()`, update types
- [x] 4.5 Migrate `change_password` use case: update to Account types and AccountUnitOfWork
- [x] 4.6 Migrate `create_user` → `create_account` use case: rename command/handler/port, use email instead of username, AccountService, AccountUnitOfWork
- [x] 4.7 Migrate `current_user` → `current_account` use case: use AccountRepository, return account data (id, email, role, is_active)
- [x] 4.8 Migrate `list_users` → `list_accounts` use case: use AccountRepository, return AccountQueryModel
- [x] 4.9 Migrate `activate_user` → `activate_account` use case: update types
- [x] 4.10 Migrate `deactivate_user` → `deactivate_account` use case: update types
- [x] 4.11 Migrate `set_user_password` → `set_account_password` use case: update types
- [x] 4.12 Migrate `grant_admin` use case: update to Account types
- [x] 4.13 Migrate `revoke_admin` use case: update to Account types
- [x] 4.14 Migrate `refresh_token` use case: update to Account types
- [x] 4.15 Add `__init__.py` files for all account application packages

## 5. Account Bounded Context - Infrastructure Layer (`src/account/infrastructure/`)

- [x] 5.1 Create `account/infrastructure/persistence/mappers/account.py` with `accounts` table definition and imperative mapper (email VARCHAR(255), accountrole enum)
- [x] 5.2 Create `account/infrastructure/persistence/sqla_account_repository.py` implementing AccountRepository (get_by_email replaces get_by_username)
- [x] 5.3 Create `account/infrastructure/persistence/sqla_account_unit_of_work.py` implementing AccountUnitOfWork (catch IntegrityError → EmailAlreadyExistsError)
- [x] 5.4 Move refresh token persistence to `account/infrastructure/`: refresh token mapper (rename user_id → account_id), SqlaRefreshTokenRepository, SqlaAuthUnitOfWork
- [x] 5.5 Move security adapters to `account/infrastructure/security/`: BcryptPasswordHasher, JwtAccessTokenProcessor, RefreshTokenService (update UserId → AccountId), RefreshToken dataclass, RefreshTokenRepository protocol, access_revoker, user_id_generator → account_id_generator
- [x] 5.6 Create `account/infrastructure/http/routers/account_router.py` with all `/api/v1/accounts/` routes (self-service + admin)
- [x] 5.7 Migrate account HTTP controllers: signup (email), login (email), change_password, refresh, current_account (/me), create_account, list_accounts, set_account_password, activate_account, deactivate_account, grant_admin, revoke_admin
- [x] 5.8 Create `account/infrastructure/events/handlers/` with `LogAccountCreated` handler
- [x] 5.9 Add `__init__.py` files for all account infrastructure packages

## 6. Core Bounded Context - Domain Layer (`src/core/domain/`)

- [x] 6.1 Create `core/` directory structure: `core/domain/profile/`, `core/application/`, `core/infrastructure/`
- [x] 6.2 Create `core/domain/profile/value_objects.py` with `ProfileId` (UUID wrapper) and `Username` (move from old user, same validation)
- [x] 6.3 Create `core/domain/profile/events.py` with `ProfileCreated` and `UsernameChanged`
- [x] 6.4 Create `core/domain/profile/errors.py` with `ProfileNotFoundByIdError`, `ProfileNotFoundByAccountIdError`, `UsernameAlreadyExistsError`
- [x] 6.5 Create `core/domain/profile/ports.py` with `ProfileIdGenerator`
- [x] 6.6 Create `core/domain/profile/repository.py` with `ProfileRepository` protocol and `ProfileQueryModel`, `ListProfilesQM`
- [x] 6.7 Create `core/domain/profile/entity.py` with `Profile` aggregate root (fields: id_, account_id, username; methods: create, set_username)
- [x] 6.8 Add `__init__.py` files for all core domain packages

## 7. Core Bounded Context - Application Layer (`src/core/application/`)

- [x] 7.1 Create `core/application/shared/core_unit_of_work.py` with `CoreUnitOfWork` protocol
- [x] 7.2 Create `core/application/get_my_profile/` use case (handler loads profile by current account_id, returns profile data)
- [x] 7.3 Create `core/application/set_username/` use case (handler loads profile, calls set_username, commits via CoreUnitOfWork)
- [x] 7.4 Create `core/application/list_profiles/` use case (handler returns paginated profiles, requires admin permission)
- [x] 7.5 Add `__init__.py` files for all core application packages

## 8. Core Bounded Context - Infrastructure Layer (`src/core/infrastructure/`)

- [x] 8.1 Create `core/infrastructure/persistence/mappers/profile.py` with `profiles` table definition and imperative mapper (nullable username)
- [x] 8.2 Create `core/infrastructure/persistence/sqla_profile_repository.py` implementing ProfileRepository
- [x] 8.3 Create `core/infrastructure/persistence/sqla_core_unit_of_work.py` implementing CoreUnitOfWork (catch IntegrityError → UsernameAlreadyExistsError)
- [x] 8.4 Create `core/infrastructure/http/routers/profile_router.py` with all `/api/v1/profiles/` routes
- [x] 8.5 Create profile HTTP controllers: get_my_profile (/me GET), set_username (/me/username PUT), list_profiles (/ GET)
- [x] 8.6 Create `core/infrastructure/events/handlers/create_profile_on_account_created.py` with `CreateProfileOnAccountCreated` handler
- [x] 8.7 Create `core/infrastructure/security/profile_id_generator.py` with UUID7-based ProfileIdGenerator
- [x] 8.8 Add `__init__.py` files for all core infrastructure packages

## 9. DI Composition Root & App Config

- [x] 9.1 Restructure DI providers by bounded context: AccountDomainProvider, AccountApplicationProvider, AccountInfrastructureProvider, CoreDomainProvider, CoreApplicationProvider, CoreInfrastructureProvider, SharedProvider
- [x] 9.2 Update app factory to register account_router and profile_router, remove old user_router and account_router
- [x] 9.3 Update `auto_discover_handlers()` call at startup to scan both contexts
- [x] 9.4 Update settings if needed (no CookiesSettings changes needed, already removed)

## 10. Cleanup

- [x] 10.1 Delete old `src/domain/` directory (user aggregate, shared domain types now in shared kernel)
- [x] 10.2 Delete old `src/application/` directory (use cases moved to bounded contexts)
- [x] 10.3 Delete old `src/infrastructure/` directory (adapters moved to bounded contexts and shared)
- [x] 10.4 Update all import paths across the codebase
- [x] 10.5 Verify all `__init__.py` files exist for proper Python packaging
- [x] 10.6 Run tests and fix any remaining import or type errors
