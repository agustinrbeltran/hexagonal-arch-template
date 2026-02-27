## 1. Dependencies & Project Setup

- [x] 1.1 Add `httpx` to the test dependency group in `pyproject.toml`
- [x] 1.2 Create directory structure: `tests/app/integration/api/account/`, `tests/app/integration/api/profile/`

## 2. Integration Test Infrastructure

- [x] 2.1 Create `FakeIdentityProvider` implementing `IdentityProvider` with configurable `AccountId` and `set_current_account()` method
- [x] 2.2 Create `TestSupabaseProvider` (Dishka Provider) that overrides all Supabase auth adapters (`AccountProvisioner`, `PasswordResetter`, `TokenPairIssuer`, `TokenPairRefresher`, `AccessRevoker`) with `create_autospec` mocks
- [x] 2.3 Create `TestRepositoryProvider` (Dishka Provider) that overrides `AccountRepository`, `ProfileRepository`, `AccountUnitOfWork`, `CoreUnitOfWork`, `EventDispatcher` with `create_autospec` mocks
- [x] 2.4 Create `TestAuthProvider` (Dishka Provider) that provides `FakeIdentityProvider` as `IdentityProvider` and a pass-through `AuthorizationGuard`
- [x] 2.5 Create test-specific lifespan that calls `_map_tables()` and `auto_discover_handlers()` but skips `OutboxRelay`
- [x] 2.6 Create programmatic `AppSettings` fixture with dummy values (no TOML files)
- [x] 2.7 Create `tests/app/integration/conftest.py` with test app factory fixture using `make_app()` with override providers
- [x] 2.8 Create `tests/app/integration/api/conftest.py` with `httpx.AsyncClient` fixture, `auth_headers` fixture, and mock accessor fixtures

## 3. Shared Endpoint Tests

- [x] 3.1 Create `tests/app/integration/api/test_health.py` — GET /api/v1/health returns 200 with `{"status": "ok"}`
- [x] 3.2 Create `tests/app/integration/api/test_root.py` — GET / returns 307 redirect to /docs/

## 4. Account Endpoint Tests — Public

- [x] 4.1 Create `tests/app/integration/api/account/test_signup.py` — happy path (201), duplicate email (409), invalid email (400)
- [x] 4.2 Create `tests/app/integration/api/account/test_login.py` — happy path (200 with tokens), invalid credentials (401)
- [x] 4.3 Create `tests/app/integration/api/account/test_refresh.py` — happy path (200 with new tokens)

## 5. Account Endpoint Tests — Protected (Self)

- [x] 5.1 Create `tests/app/integration/api/account/test_current_account.py` — authenticated (200), unauthenticated (403)
- [x] 5.2 Create `tests/app/integration/api/account/test_change_password.py` — authenticated (204), unauthenticated (403)

## 6. Account Endpoint Tests — Protected (Admin)

- [x] 6.1 Create `tests/app/integration/api/account/test_create_account.py` — admin creates (201), unauthenticated (403)
- [x] 6.2 Create `tests/app/integration/api/account/test_list_accounts.py` — default pagination (200), custom pagination, unauthenticated (403)
- [x] 6.3 Create `tests/app/integration/api/account/test_set_password.py` — authenticated (204), unauthenticated (403)
- [x] 6.4 Create `tests/app/integration/api/account/test_grant_admin.py` — authenticated (204), unauthenticated (403)
- [x] 6.5 Create `tests/app/integration/api/account/test_revoke_admin.py` — authenticated (204), unauthenticated (403)
- [x] 6.6 Create `tests/app/integration/api/account/test_activate.py` — authenticated (204), unauthenticated (403)
- [x] 6.7 Create `tests/app/integration/api/account/test_deactivate.py` — authenticated (204), unauthenticated (403)

## 7. Profile Endpoint Tests

- [x] 7.1 Create `tests/app/integration/api/profile/test_get_my_profile.py` — authenticated (200 with fields), unauthenticated (403)
- [x] 7.2 Create `tests/app/integration/api/profile/test_update_profile.py` — authenticated PUT (204), unauthenticated (403)
- [x] 7.3 Create `tests/app/integration/api/profile/test_patch_profile.py` — authenticated PATCH (204), unauthenticated (403)
- [x] 7.4 Create `tests/app/integration/api/profile/test_list_profiles.py` — default pagination (200), unauthenticated (403)

## 8. Account Persistence Unit Tests

- [x] 8.1 Create `tests/app/unit/account/infrastructure/persistence/test_sqla_account_repository.py` — save (merge called with correct record), get_by_id (found, not found, for_update), get_by_email (found, not found), get_all (paginated results, invalid sorting field), error wrapping
- [x] 8.2 Create `tests/app/unit/account/infrastructure/persistence/test_sqla_account_unit_of_work.py` — commit (flush + commit order), IntegrityError → DataMapperError, SQLAlchemyError → DataMapperError, rollback delegates

## 9. Verification

- [x] 9.1 Run `make code.check` (lint + test) and ensure all existing + new tests pass
