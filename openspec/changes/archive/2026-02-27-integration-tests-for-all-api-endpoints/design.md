## Context

The project uses FastAPI + Dishka DI + SQLAlchemy 2.0 + Supabase Auth. There are 179 unit tests covering domain entities, value objects, use case handlers, and one integration test for config loading. Zero tests exercise the HTTP layer — routing, DI wiring, request/response serialization, auth middleware, or error mapping. Developers must manually verify every endpoint after changes.

The `make_app(*di_providers, settings=...)` entry point already supports passing additional Dishka providers that override production bindings — this is the hook for test infrastructure.

## Goals / Non-Goals

**Goals:**
- Automated regression safety net for all 18 API endpoints
- Test HTTP routing, request validation, response serialization, DI wiring, auth middleware, error mapping
- Mock at the repository/auth-adapter boundary so domain + use case logic is exercised
- Fill the missing account persistence unit test gap
- Run fast without external dependencies (no running DB or Supabase required)

**Non-Goals:**
- Full E2E tests against a running server or real Supabase
- Database-level integration tests with real SQL (future `@slow` test tier)
- Performance or load testing
- Changing any production code

## Decisions

### 1. Mock at repository level, not use case level

**Choice:** Override repository Protocols (AccountRepository, ProfileRepository) and Supabase auth adapters with mocks. Use cases run with real logic.

**Rationale:** Unit tests already cover use case handlers in isolation. Integration tests should verify the layer above: that HTTP requests wire through DI into real use case orchestration, domain validation fires, and errors map to correct HTTP statuses. Mocking at use case level would skip too much of the stack.

**Alternative considered:** Mock at use case Protocol level — simpler but only tests HTTP serialization, missing DI wiring and domain logic bugs.

### 2. FakeIdentityProvider instead of real JWT validation

**Choice:** Provide a `FakeIdentityProvider` that returns a configurable `AccountId` from any Bearer token. No real JWT signing/verification in tests.

**Rationale:** JWT verification depends on Supabase JWKS or a shared secret. The identity provider Protocol is the clean boundary. Tests control "who is logged in" by calling `fake_identity.set_current_account(account_id)`. Protected endpoints still reject missing `Authorization` headers via FastAPI's `HTTPBearer` dependency.

**Alternative considered:** Generate test JWTs with a test secret — more realistic but couples tests to JWT implementation details and adds setup complexity.

### 3. Test-specific lifespan (map tables, skip relay)

**Choice:** Replace the production lifespan with a test lifespan that calls `_map_tables()` and `auto_discover_handlers()` but does not start the `OutboxRelay` background task.

**Rationale:** Table mapping is needed for converter/record classes to work. Event handler discovery is needed for handler resolution. The outbox relay requires a real DB connection and runs as a background asyncio task — unnecessary complexity for HTTP-layer tests where event dispatch is mocked.

### 4. httpx.AsyncClient with ASGITransport

**Choice:** Use `httpx.AsyncClient` with `ASGITransport(app=app)` for async test requests.

**Rationale:** The app uses async handlers throughout. `httpx.AsyncClient` provides native async HTTP testing without spawning a server. FastAPI officially recommends this pattern. It's the standard for `pytest-asyncio` test suites.

### 5. Dishka provider overrides via extra providers

**Choice:** Create test-only `Provider` subclasses (`TestRepositoryProvider`, `TestSupabaseProvider`, `TestAuthProvider`) and pass them to `make_app()` where later providers override earlier bindings.

**Rationale:** Dishka's `make_async_container` applies providers in order — last provider wins for duplicate bindings. The existing `make_app(*di_providers)` signature was designed for exactly this. No patching or monkey-patching required.

### 6. Programmatic test settings

**Choice:** Build `AppSettings` programmatically in fixtures with dummy values. No `config/test/config.toml` file.

**Rationale:** Test settings need minimal valid structure (dummy DB URL, dummy JWT secret). A TOML file adds a maintenance burden and can drift. Programmatic construction makes test assumptions explicit and visible in conftest.py.

### 7. Test file organization mirrors API structure

**Choice:** `tests/app/integration/api/{context}/test_{endpoint}.py` with shared conftest fixtures.

**Rationale:** Mirrors the source structure. Each endpoint gets its own test file for clarity. Shared fixtures (client, auth helpers, mock providers) live in conftest.py files at appropriate levels.

## Risks / Trade-offs

- **[Mock drift]** Mocked repositories may accept calls that real implementations reject → Mitigate with `create_autospec()` which enforces method signatures, and complement with future DB-level integration tests.
- **[Lifespan divergence]** Test lifespan skips relay, may miss startup bugs → Mitigate by keeping test lifespan minimal (only skip relay, keep everything else real).
- **[DI override fragility]** Adding new providers in production may require updating test overrides → Mitigate by overriding at the Protocol level (interfaces), not implementations. New providers for the same Protocol automatically get overridden.
