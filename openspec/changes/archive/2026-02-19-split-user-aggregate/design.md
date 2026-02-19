## Context

The project currently uses a single `User` aggregate that combines authentication concerns (username/password, role, active status) with user metadata. All code lives under a flat `src/domain/`, `src/application/`, `src/infrastructure/` structure with no bounded context separation.

The current User aggregate is used by 12 use cases, has 5 domain events, a permission framework, and is persisted via SQLAlchemy imperative mapping to a `users` table. Login is username-based.

## Goals / Non-Goals

**Goals:**
- Split User into Account (auth/access) and Profile (metadata) aggregates
- Introduce bounded context directory structure: `src/account/`, `src/core/`, `src/shared/`
- Replace username-based login with email-based login
- Establish cross-context communication via domain events (AccountCreated → Profile creation)
- Each bounded context has its own UnitOfWork implementation
- Maintain all existing authorization/permission behavior under the Account aggregate

**Non-Goals:**
- Extracting bounded contexts into separate services or databases (single DB, single process)
- Implementing an anti-corruption layer between contexts (shared kernel with `AccountId` is sufficient for a monolith)
- Adding profile fields beyond username (bio, avatar, etc. are future work)
- Changing the permission/authorization framework design (only renaming)
- Modifying the refresh token or JWT infrastructure beyond renaming `UserId` → `AccountId`

## Decisions

### 1. Role stays with Account, not Profile

**Decision**: `AccountRole` (SUPER_ADMIN, ADMIN, USER) remains on the Account aggregate.

**Rationale**: Role governs authorization decisions (what you can do), not identity metadata (who you are). The entire permission framework (`CanManageSubordinate`, `CanManageRole`, `SUBORDINATE_ROLES`) operates on the acting user's role. Moving role to Profile would require loading two aggregates for every authorization check, coupling auth decisions to a different consistency boundary.

**Alternative considered**: Role on Profile — rejected because it couples authorization to the wrong aggregate and forces cross-aggregate reads on every protected operation.

### 2. Shared Kernel for cross-context types

**Decision**: `src/shared/` contains base domain classes (`Entity`, `AggregateRoot`, `ValueObject`, `DomainEvent`), the `AccountId` value object, `IdentityProvider` port, event dispatcher infrastructure, pagination/sorting primitives, and shared application ports.

**Rationale**: Both contexts need these types. In a monolith, a shared kernel avoids duplication without the overhead of an anti-corruption layer. `AccountId` is in the shared kernel because Profile references it as a foreign key and `IdentityProvider` returns it.

**Alternative considered**: Each context defines its own ID type (e.g., Core uses `OwnerAccountId`) — rejected as unnecessary indirection in a monolith.

### 3. One UnitOfWork per bounded context

**Decision**: `AccountUnitOfWork` and `CoreUnitOfWork` as separate protocol + implementation pairs, even though they use the same database.

**Rationale**: Different bounded contexts = different consistency boundaries. Even sharing a database, they should manage their own transactions independently. This also future-proofs for eventual database separation.

The existing `AuthUnitOfWork` remains Account-only (manages auth session/refresh token persistence).

### 4. Email replaces Username for authentication

**Decision**: The `Account` aggregate uses `Email` as the login identifier. `Username` moves to the `Profile` aggregate as optional metadata (nullable, set after signup).

**Rationale**: Email is the industry standard for account identification. Username becomes a display-name concern belonging to Profile. Signup only requires email + password; username is set later via `/api/v1/profiles/me/username`.

### 5. Unified `/accounts/` API path

**Decision**: Both self-service (`/me`) and admin operations live under `/api/v1/accounts/`. No singular/plural distinction.

**Rationale**: Simpler routing, single resource concept. The `/me` sub-path disambiguates self-service from admin operations on other accounts.

### 6. Cross-context event handling for Profile creation

**Decision**: `AccountCreated` event is dispatched after `AccountUnitOfWork.commit()`. The `CreateProfileOnAccountCreated` handler in Core BC creates an empty Profile with a new `ProfileId`, the `account_id` from the event, and `username=None`. This runs in a separate transaction via `CoreUnitOfWork`.

**Rationale**: Keeps contexts loosely coupled. The handler is in Core's infrastructure because it's Core's responsibility to create its own aggregate.

**Trade-off**: Eventual consistency — if Profile creation fails, there's an Account without a Profile. Acceptable because Profile starts empty and `GET /profiles/me` returns 200 with null username regardless.

### 7. Directory structure: flat context directories

**Decision**:
```
src/
  shared/domain/          ← base classes, AccountId, IdentityProvider
  shared/infrastructure/  ← event dispatcher, registry
  account/domain/         ← Account aggregate, permissions, services
  account/application/    ← all account use cases
  account/infrastructure/ ← persistence, security, HTTP, events
  core/domain/            ← Profile aggregate
  core/application/       ← profile use cases
  core/infrastructure/    ← persistence, HTTP, events
```

Each context mirrors the hexagonal architecture layers internally.

### 8. Event handler auto-discovery across contexts

**Decision**: `auto_discover_handlers()` must scan both `account.infrastructure.events.handlers` and `core.infrastructure.events.handlers` packages.

**Rationale**: The cross-context handler (`CreateProfileOnAccountCreated`) lives in Core's infrastructure but handles an Account domain event. The discovery mechanism must be context-aware.

## Risks / Trade-offs

- **Eventual consistency between Account and Profile** → Acceptable for empty profiles. If Profile creation fails, the account still functions. Can add a reconciliation job later if needed.
- **Large rename/restructure touches every file** → Mitigate by doing the restructure methodically: shared kernel first, then Account BC, then Core BC. Run tests after each phase.
- **DI composition root complexity increases** → The Dishka container must wire providers from both contexts. Organize providers by context (AccountProvider, CoreProvider, SharedProvider).
- **Email uniqueness constraint** → The `accounts` table needs a UNIQUE constraint on `email` (replacing the one on `username`). The `AccountUnitOfWork` must catch `IntegrityError` and raise `EmailAlreadyExistsError`.
- **Breaking API changes** → All consumers must update. No backward-compatible shim (clean break per user's preference).

## Migration Plan

1. Apply database migration: rename `users` → `accounts`, `username` → `email` (expand to VARCHAR(255)), rename enum `userrole` → `accountrole`, create `profiles` table
2. Deploy updated application code with new directory structure and API paths
3. No rollback strategy for the DB migration needed in a template project — this is a clean architectural evolution

## Open Questions

None — all decisions were resolved during exploration.
