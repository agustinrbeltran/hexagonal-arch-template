## Why

The codebase has three categories of architecture layer violations that contradict the hexagonal/clean architecture dependency rules: domain imports from infrastructure, application handlers depend on concrete implementations instead of ports, and a cross-context domain coupling bypasses bounded context boundaries. These violations erode the architecture's guarantees and should be fixed before they compound further.

## What Changes

- Move `register_event` decorator from `shared/infrastructure/events/registry.py` to `shared/domain/event_registry.py` so domain event files no longer import from infrastructure
- Replace all 9 handler dependencies on `CurrentAccountHandler` (concrete) with `CurrentAccountUseCase` (port), and remove the `provide_all(CurrentAccountHandler)` line from the DI container
- Introduce an `AuthorizationGuard` port in `shared/domain/ports/` and implement it in `account/infrastructure/`, then refactor `ListProfilesHandler` to use the guard instead of importing `AccountRole` and `AccountRepository` directly from the Account bounded context

## Capabilities

### New Capabilities
- `authorization-guard`: A shared domain port that allows any bounded context to check admin authorization without coupling to the Account domain

### Modified Capabilities
- `event-type-registration`: Move `register_event` decorator to shared domain layer (currently spec says it lives in `shared/infrastructure/events/registry.py`)
- `application-use-cases`: Handlers must depend on use case ports (ABCs), not on concrete handler implementations
- `bounded-context-structure`: Enforce the existing "no cross-context domain imports" requirement that `ListProfilesHandler` currently violates

## Impact

- **Domain layer** (`account/domain/account/events.py`, `core/domain/profile/events.py`): Import path changes for `register_event`
- **Application layer** (9 handler files in `account/application/`): Type annotation changes from `CurrentAccountHandler` → `CurrentAccountUseCase`
- **Application layer** (`core/application/list_profiles/handler.py`): Replace `AccountRepository` + `AccountRole` imports with `AuthorizationGuard` port
- **Infrastructure layer** (`shared/infrastructure/events/registry.py`): `register_event` and `_event_type_registry` move out; `handles`, `get_handlers_for`, `get_event_class`, `auto_discover_handlers` remain
- **Infrastructure layer** (new file in `account/infrastructure/`): `AuthorizationGuard` implementation
- **DI container** (`shared/infrastructure/config/di/application.py`): Remove `provide_all(CurrentAccountHandler)`, add `AuthorizationGuard` provider
- **Tests**: Any tests mocking `CurrentAccountHandler` or importing `register_event` will need import path updates
