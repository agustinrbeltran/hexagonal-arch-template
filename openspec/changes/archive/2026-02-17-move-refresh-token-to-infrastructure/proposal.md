## Why

The `RefreshToken` concept currently lives in `src/domain/refresh_token/` as if it were a domain aggregate, but per DDD tactical patterns it is not: it has no lifecycle mutations, no domain events, no invariants, and no child entities. It is a security/auth infrastructure artifact — created, looked up, and deleted — with zero domain behavior. Keeping it in the domain layer misrepresents the architecture and pollutes the domain with infrastructure concerns.

## What Changes

- **Remove `src/domain/refresh_token/`** entirely (entity, repository, services, errors)
- **Move `RefreshToken` dataclass, `RefreshTokenRepository`, `RefreshTokenService`, and errors** into `src/infrastructure/security/`
- **Introduce application-layer ports** (`TokenPairIssuer`, `TokenPairRefresher`) so `LogInHandler` and `RefreshTokenHandler` depend on abstractions instead of a concrete domain service
- **Update DI providers** to wire the new ports to the infrastructure implementation
- **Update imports** in `access_revoker.py`, persistence mappers, and all consumers
- **Rename domain-level errors** to infrastructure-level errors (same classes, new location)

## Capabilities

### New Capabilities
- `token-management-ports`: Application-layer port abstractions (`TokenPairIssuer`, `TokenPairRefresher`) that the application layer depends on, implemented by infrastructure

### Modified Capabilities
- `infrastructure-adapters`: Security adapters section gains RefreshToken-related modules (service, repository, entity, errors) that previously lived in domain
- `application-use-cases`: `log_in` and `refresh_token` handlers depend on new ports instead of `RefreshTokenService` directly

## Impact

- **Removed code**: `src/domain/refresh_token/` (4 modules: entity.py, repository.py, services.py, errors.py)
- **New code**: Application ports for token management, relocated infrastructure modules
- **Modified code**: `LogInHandler`, `RefreshTokenHandler`, `RefreshTokenAccessRevoker`, DI providers, persistence mapper imports
- **No API changes**: All HTTP endpoints, request/response schemas, and behavior remain identical
- **No test behavior changes**: Tests will need import path updates but assertions stay the same
