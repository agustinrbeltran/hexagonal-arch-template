## Why

The project has 179 unit tests but zero HTTP-level integration tests. After every feature implementation or refactor, developers must manually test each endpoint (via curl, Postman, etc.) to verify the API surface is intact. This is error-prone and slow. A regression safety net that automatically validates all 18 API endpoints — routing, DI wiring, request validation, response serialization, auth middleware, and error mapping — is needed to catch breakage early.

## What Changes

- Add integration test infrastructure: test app factory with Dishka provider overrides, mock providers for external boundaries (Supabase Auth, DB repositories), a configurable `FakeIdentityProvider` for auth, and a test-specific lifespan that skips the outbox relay.
- Add integration tests for all 18 API endpoints covering happy paths, auth rejection, input validation, and domain error-to-HTTP-status mapping (~70-90 tests).
- Add missing account persistence unit tests (`SqlaAccountRepository`, `SqlaAccountUnitOfWork`) following the existing core profile persistence test pattern (~15-20 tests).
- Add `httpx` to the test dependency group in `pyproject.toml`.

## Capabilities

### New Capabilities
- `api-integration-testing`: Integration test infrastructure and endpoint tests for the full API surface using TestClient + real Dishka DI + mocked repository/auth boundaries.
- `account-persistence-unit-testing`: Unit tests for `SqlaAccountRepository` and `SqlaAccountUnitOfWork` following the established core persistence test patterns.

### Modified Capabilities

_(none — no existing spec-level requirements change)_

## Impact

- **New files**: `tests/app/integration/` directory tree (~20 test files + conftest fixtures)
- **New files**: `tests/app/unit/account/infrastructure/persistence/` (~2 test files)
- **Modified**: `pyproject.toml` (add `httpx` to test dependencies)
- **No production code changes** — this is purely additive test infrastructure
