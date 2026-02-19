# Proposal: Fix Unit Test Structure

## Problem

After the major refactor from `User`-centric to `Account`/`Profile` bounded contexts, the unit test suite has two issues:

1. **Stale file/folder names** — Several test files and factories still use old `User`-era naming (`test_user.py`, `test_username.py`, `test_user_role.py`, `user_entity.py`) even though the domain concepts they test have been renamed (`Account`, `Email`, `AccountRole`).

2. **Missing test coverage** — 13 out of 15 application handlers have zero unit tests. Only `LogInHandler` and `RefreshTokenHandler` are tested. The entire `core` bounded context (Profile) has no tests at all — no entity tests, no value object tests, no handler tests.

3. **Flat folder structure** — The test directory doesn't reflect the bounded context organization (`account/`, `core/`, `shared/`) introduced in the refactor.

## Proposed Solution

1. **Restructure `tests/app/unit/` to mirror bounded contexts** (Option A from exploration):
   - `account/application/` — all account use case handler tests
   - `account/domain/` — Account entity, service, value object, enum tests
   - `core/application/` — all profile use case handler tests
   - `core/domain/` — Profile entity, Username value object tests
   - `shared/domain/` — Entity base, ValueObject base, authorization tests
   - `shared/infrastructure/` — password hasher, config/settings tests

2. **Rename stale test files** to match current domain concepts.

3. **Add missing handler tests** for all 13 untested handlers.

4. **Add missing domain tests** for the `core` bounded context (Profile entity, Username VO).

5. **Add a Profile factory** for core handler tests.

## Non-goals

- Integration tests are out of scope.
- No changes to source code — only test files.
- Not adding tests for infrastructure adapters (SQLAlchemy repos, HTTP controllers, etc.) beyond what already exists.
