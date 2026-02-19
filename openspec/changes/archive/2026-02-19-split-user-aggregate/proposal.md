## Why

The current `User` aggregate conflates two distinct concerns: authentication/access control (email, password, role, active status) and user metadata (username, future profile fields). This violates the Single Responsibility Principle at the aggregate level and prevents independent evolution of auth vs. profile concerns. Splitting them also introduces bounded contexts (Account and Core), establishing a foundation for proper DDD context separation across the codebase.

## What Changes

- **BREAKING**: Split the `User` aggregate into two aggregates across two bounded contexts:
  - `Account` (Account BC): holds `email` (replacing `username` for login), `password_hash`, `role`, `is_active`
  - `Profile` (Core BC): holds `username` (nullable, set after signup)
- **BREAKING**: Restructure `src/` into bounded context directories: `src/account/`, `src/core/`, `src/shared/`
  - Each context contains its own `domain/`, `application/`, `infrastructure/` layers
  - `src/shared/` becomes the shared kernel (base classes, cross-cutting ports, event infrastructure)
- **BREAKING**: Replace `username` with `email` in signup and login flows
- Introduce cross-context domain event: `AccountCreated` triggers `CreateProfileOnAccountCreated` handler in Core BC, creating an empty profile
- **BREAKING**: Rename all User-related types, events, errors, and repositories to Account-prefixed equivalents
- **BREAKING**: API restructure:
  - `/api/v1/account/` → `/api/v1/accounts/` (unified singular path for both self-service and admin)
  - `/api/v1/users/` → removed, admin operations move under `/api/v1/accounts/`
  - New `/api/v1/profiles/` resource for profile self-service and admin listing
- Separate `UnitOfWork` per bounded context: `AccountUnitOfWork`, `CoreUnitOfWork`

## Capabilities

### New Capabilities
- `account-aggregate`: Account aggregate root with email-based identity, password, role, and activation. Replaces the auth/access subset of the former user-aggregate.
- `profile-aggregate`: Profile aggregate root with username and account reference. Created empty on account creation via domain event.
- `bounded-context-structure`: Directory structure organizing code into Account BC, Core BC, and shared kernel under `src/`.

### Modified Capabilities
- `application-use-cases`: Rename and reorganize all use cases into their respective bounded contexts. Signup/login change from username to email. New use cases: `get_my_profile`, `set_username`, `list_profiles`.
- `domain-events`: `AccountCreated` replaces `UserCreated`. New cross-context event handler `CreateProfileOnAccountCreated`.
- `domain-event-handler-registry`: Auto-discovery must scan handlers in both `account` and `core` context infrastructure.
- `infrastructure-adapters`: Repositories, mappers, HTTP controllers, and routers restructured into BC directories. New `profiles` table migration. `accounts` table replaces `users` table.
- `token-management-ports`: `UserId` references become `AccountId` from shared kernel.
- `refresh-token`: `UserId` references become `AccountId`.
- `jwt-bearer-auth`: Identity provider moves to shared kernel. Returns `AccountId`.
- `domain-model`: Base classes move to `src/shared/domain/`. `AccountId` added to shared kernel.
- `user-aggregate`: **REMOVED** - replaced by `account-aggregate` and `profile-aggregate`.

## Impact

- **Database**: Migration to rename `users` → `accounts`, `username` → `email` (VARCHAR(255)), create `profiles` table, rename `userrole` → `accountrole` enum
- **API**: All endpoints change paths and request/response shapes. Breaking change for all API consumers.
- **Directory structure**: Every existing file under `src/` moves into `src/account/`, `src/core/`, or `src/shared/`
- **DI composition root**: Must be restructured to provide dependencies from both bounded contexts
- **Tests**: All test files need updating to reflect new paths, names, and aggregate boundaries
- **Auth flow**: Login/signup switch from username to email
