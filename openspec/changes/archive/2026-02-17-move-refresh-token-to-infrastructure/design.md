## Context

The `src/domain/refresh_token/` package currently contains: `entity.py` (a plain dataclass), `repository.py` (a protocol), `services.py` (RefreshTokenService with token issuance, rotation, and revocation logic), and `errors.py`. These are treated as domain-layer artifacts despite having no DDD characteristics — no lifecycle mutations, no domain events, no aggregate invariants. The application handlers (`LogInHandler`, `RefreshTokenHandler`) depend directly on the concrete `RefreshTokenService` class from the domain layer.

The project uses a layered architecture: domain (pure business) → application (orchestration) → infrastructure (adapters). Dependency rule: inner layers never import outer layers. Currently, `RefreshTokenService` sits in domain but depends on infrastructure-defined protocols (`RefreshTokenIdGenerator`, `AccessTokenEncoder`), creating an awkward coupling where the domain service is really an infrastructure coordinator.

## Goals / Non-Goals

**Goals:**
- Remove `src/domain/refresh_token/` entirely — the domain layer should contain only true business concepts
- Relocate all refresh-token artifacts to `infrastructure/security/` where they belong alongside existing JWT/bcrypt adapters
- Introduce thin application-layer ports (`TokenPairIssuer`, `TokenPairRefresher`) so application handlers respect the dependency rule
- Preserve all existing behavior — zero functional changes, only structural

**Non-Goals:**
- Changing RefreshToken's data model or storage mechanism
- Modifying HTTP API contracts or response schemas
- Refactoring RefreshTokenService internals (rotation logic, expiry logic)
- Moving the persistence layer (SQLAlchemy mapper/repo impl stays in `infrastructure/persistence/`)
- Removing the `application/refresh_token/` use case directory

## Decisions

### 1. Application-layer ports over domain ports

**Decision**: Create `TokenPairIssuer` and `TokenPairRefresher` protocols in the application layer, not the domain layer.

**Rationale**: These ports serve application-layer orchestration (use case handlers). The domain layer has no concept of "tokens" — it deals with Users, permissions, and business rules. Placing these ports in `application/shared/` keeps the domain clean and follows the pattern already established by `UnitOfWork` in `application/shared/`.

**Alternative considered**: Keeping ports in `domain/user/ports.py` alongside `AccessRevoker`. Rejected because token management is not a User domain concern — `AccessRevoker` is there because revoking access is something the User aggregate's lifecycle triggers (e.g., deactivation). Token issuance is purely an auth infrastructure operation invoked by application use cases.

### 2. Single RefreshTokenService implements both ports

**Decision**: The existing `RefreshTokenService` (relocated to `infrastructure/security/`) implements both `TokenPairIssuer` and `TokenPairRefresher`.

**Rationale**: The service already has both `issue_token_pair()` and `refresh()` methods. Splitting into two classes would add complexity without benefit — they share the same dependencies (repository, ID generator, encoder, config). ISP is satisfied at the consumer level via the separate port protocols.

### 3. Errors move to infrastructure/security/errors.py

**Decision**: `RefreshTokenNotFoundError` and `RefreshTokenExpiredError` move to `infrastructure/security/errors.py` (which already exists). They stop extending `DomainError` and instead become plain exceptions or extend a new `SecurityError` base.

**Rationale**: These are not domain errors — they're infrastructure-level auth failures. The HTTP error handler already maps specific exception types to HTTP status codes, so the change is transparent to the API layer.

**Alternative considered**: Keeping them as `DomainError` subclasses in the new location. Rejected because that would require infrastructure importing domain base classes for non-domain errors, muddying the conceptual boundary.

### 4. Persistence mapper and repository stay in infrastructure/persistence/

**Decision**: `infrastructure/persistence/sqla_refresh_token_repository.py` and `infrastructure/persistence/mappers/refresh_token.py` remain in their current locations. Only their import paths for the entity and repository protocol change.

**Rationale**: The persistence layer already has a clear structure. The SQLAlchemy repo implements the relocated `RefreshTokenRepository` protocol from `infrastructure/security/`. This is an internal infrastructure dependency (infra → infra), which is perfectly acceptable.

### 5. AccessRevoker stays in domain/user/ports.py

**Decision**: The `AccessRevoker` protocol remains in `domain/user/ports.py`. Its implementation (`RefreshTokenAccessRevoker`) stays in `infrastructure/security/` with updated imports.

**Rationale**: `AccessRevoker` is a legitimate domain port — "revoking user access" is a business concept that the User aggregate's lifecycle depends on (deactivation triggers revocation). The fact that it's *implemented* via refresh token deletion is an infrastructure detail.

## Risks / Trade-offs

- **Import churn across test files** → Manageable: most tests import from application ports or domain, not from the relocated modules directly. Test factories and mocks will need import updates.
- **Previous delta spec for refresh-token (from cookie-to-jwt-auth change) was never synced to main specs** → This change effectively supersedes that spec. The new spec files will define the relocated structure as the canonical spec.
- **RefreshTokenRepository protocol moves from domain to infrastructure** → This means the persistence layer imports from a sibling infrastructure package. Acceptable: both are infrastructure adapters, and the repository protocol is now an internal contract rather than a domain port.
