## Context

The README.md was last updated when the project used a flat layer-first structure (`src/domain/`, `src/application/`, `src/infrastructure/`) with a single `User` aggregate. The codebase has since been refactored to:

1. **Bounded-context-first** organization: `src/account/`, `src/core/`, `src/shared/`
2. **User aggregate split** into `Account` (identity, auth, roles) and `Profile` (username, display data)
3. **Cross-context integration** via domain events (`AccountCreated` → `CreateProfileOnAccountCreated`)
4. **New API routes**: `/api/v1/accounts/` and `/api/v1/profiles/` (previously `/api/v1/account/` + `/api/v1/users/`)
5. **Value object changes**: `Username` → `Email` (on Account), `Username` remains on Profile; `UserId` → `AccountId` (shared) + `ProfileId`

The README is ~2040 lines with extensive code examples, ASCII diagrams, and references to 15+ doc images. All domain/application/infrastructure examples reference the old `User` entity, `UserRepository`, `UserService`, etc.

## Goals / Non-Goals

**Goals:**
- README accurately reflects the bounded-context-first architecture
- All code examples use current entity/VO/event/service names from actual codebase
- Project structure tree matches the real directory layout
- API section documents the current routes (`/accounts/`, `/profiles/`)
- Outdated doc images removed; valid conceptual diagrams kept
- Aggregate boundaries section shows both Account and Profile with cross-context event flow

**Non-Goals:**
- Regenerating or editing SVG/draw.io diagrams (the "Interactor" SVGs are conceptually valid and kept with their existing disclaimer)
- Changing the overall README structure/sections (Table of Contents stays the same shape, modulo renamed sections)
- Adding new architectural documentation beyond what exists (no new sections)
- Taking new Swagger screenshots (handlers.png removal, no replacement)

## Decisions

### D1: Remove `handlers.png`, keep all SVGs

**Decision**: Delete `docs/handlers.png`. Keep all `.svg` files.

**Rationale**: The Swagger screenshot shows old routes (`/api/v1/users/`, `/api/v1/account/logout`) that no longer exist. It would need a fresh screenshot which is out of scope. The SVG diagrams are either generic architectural concepts (onion, dependency graphs, config flow) or use "Interactor" terminology that is already disclaimed in the README text — the patterns they illustrate remain correct.

**Alternative considered**: Remove all "Interactor" SVGs too. Rejected because the architectural patterns they depict are still valid, and the README already notes the terminology evolution.

### D2: Update code examples from actual codebase

**Decision**: Replace all inline code examples with excerpts from the actual current source files.

**Rationale**: The README's code examples currently show a `User` entity, `UserRepository`, `UserService`, etc. that no longer exist. Using real code ensures accuracy and maintainability.

### D3: Restructure aggregate documentation around two bounded contexts

**Decision**: The "Aggregates in this project" section will document Account (in Account BC) and Profile (in Core BC) as separate aggregates, with a section on cross-context integration via domain events.

**Rationale**: This is the most significant architectural change — the split from one aggregate to two in different bounded contexts, communicating via events. This is the core story the README should tell.

### D4: Merge the old "Account" and "Users" API sections

**Decision**: Replace the old "Account (`/api/v1/account`)" and "Users (`/api/v1/users`)" sections with "Accounts (`/api/v1/accounts`)" and "Profiles (`/api/v1/profiles`)".

**Rationale**: The API routes have changed. All user management endpoints are now under `/accounts/`, and profile-related endpoints are under `/profiles/`.

## Risks / Trade-offs

- **Risk**: Code examples in README drift from actual code over time → **Mitigation**: Keep examples concise (key methods only, not full files) to reduce maintenance surface
- **Risk**: Removing `handlers.png` leaves no visual API overview → **Mitigation**: The text-based API section is comprehensive; readers can run the app to see Swagger UI
- **Trade-off**: Keeping "Interactor" SVGs with a disclaimer vs. regenerating them — we accept slight terminology mismatch for the pragmatic benefit of not needing to recreate draw.io diagrams
