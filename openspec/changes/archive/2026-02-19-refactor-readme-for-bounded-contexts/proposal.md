## Why

The README.md is thoroughly outdated after the major refactor that split the codebase from a layer-first organization (`src/domain/`, `src/application/`, `src/infrastructure/`) into a bounded-context-first organization (`src/account/`, `src/core/`, `src/shared/`), and split the single `User` aggregate into two separate aggregates: `Account` and `Profile`. Every section — structure tree, code examples, aggregate descriptions, API routes, and several doc images — references the old architecture.

## What Changes

- **BREAKING**: Rewrite the project structure tree to reflect bounded-context-first layout (`src/account/`, `src/core/`, `src/shared/`)
- Replace all references to `User` aggregate with `Account` aggregate and `Profile` aggregate
- Update all code examples (entity, value objects, events, repository, services, handlers) to use `Account`/`Profile` naming and actual current code
- Update the aggregate boundaries diagram (ASCII) to show both Account and Profile aggregates and their cross-context integration via domain events
- Update the API section to reflect new routes: `/api/v1/accounts/` (replaces `/account` + `/users`) and `/api/v1/profiles/` (new)
- Remove `docs/handlers.png` — shows old Swagger UI with outdated `/api/v1/users/` and `/api/v1/account/` routes
- Keep all generic/conceptual architecture SVGs (onion diagrams, dependency graphs, config flow) — they remain valid
- Keep the "Interactor" terminology SVGs with the existing disclaimer note (concepts are correct, terminology predates this project's naming)
- Update the domain layer, application layer, and infrastructure layer descriptions to reference bounded contexts instead of a flat structure
- Update value object examples (`Username` → `Email` on Account, `Username` on Profile; `UserPasswordHash` → `AccountPasswordHash`)
- Update domain events list (`UserCreated` → `AccountCreated`, `ProfileCreated`, etc.)
- Add documentation of cross-context integration pattern (Account emits `AccountCreated`, Core BC handles it to create Profile)

## Capabilities

### New Capabilities

_None — this is a documentation-only change updating existing content._

### Modified Capabilities

- `documentation`: README must reflect bounded-context-first structure, Account/Profile aggregate split, new API routes, and removal of outdated `handlers.png` image

## Impact

- **Files**: `README.md` (full rewrite of most sections), `docs/handlers.png` (removal)
- **No code changes**: This is purely a documentation refactor
- **No API changes**: The API already changed; we're just documenting reality
- **No dependency changes**
