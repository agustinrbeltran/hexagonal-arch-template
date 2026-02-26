## Context

The codebase follows hexagonal/clean architecture with two bounded contexts (`account`, `core`) and a shared kernel. The dependency rule is `Infrastructure → Application → Domain`, and bounded contexts communicate via domain events through the shared kernel.

Three violations exist today:
1. Domain event files import `register_event` from `shared.infrastructure.events.registry` — domain depends on infrastructure.
2. Nine application handlers import and type-hint `CurrentAccountHandler` (concrete) instead of `CurrentAccountUseCase` (port) — application depends on a concrete implementation rather than an abstraction.
3. `core/application/list_profiles/handler.py` imports `AccountRole` and `AccountRepository` from `account/domain/` — cross-context domain coupling.

## Goals / Non-Goals

**Goals:**
- Eliminate all domain → infrastructure imports
- Ensure all handler-to-handler dependencies go through ports (ABCs), not concrete classes
- Remove all cross-context domain imports from Core's application layer
- Maintain full test and runtime compatibility (no behavior changes)

**Non-Goals:**
- Redesigning the permission framework beyond what's needed for `ListProfilesHandler`
- Changing the event registry's internal mechanics (handler registration, auto-discovery)
- Adding new authorization checks to other use cases

## Decisions

### Decision 1: Move `register_event` to `shared/domain/event_registry.py`

**Choice:** Relocate `register_event` and `_event_type_registry` dict to a new module `shared/domain/event_registry.py`. The infrastructure module (`shared/infrastructure/events/registry.py`) re-imports from it and continues to own `handles`, `get_handlers_for`, `get_event_class`, and `auto_discover_handlers`.

**Rationale:** `register_event` is a pure decorator with zero infrastructure dependencies — it only manipulates an in-memory dict. Its placement in infrastructure was incidental. Moving it to domain is the smallest change that fixes the layer violation.

**Alternative considered:** Auto-discover event types at startup instead of using a decorator. Rejected because it adds runtime magic and changes the existing contract that `@register_event` guarantees import-time registration.

### Decision 2: Replace `CurrentAccountHandler` with `CurrentAccountUseCase` in all handler type hints

**Choice:** In all 9 handler constructors, change the type annotation from `CurrentAccountHandler` to `CurrentAccountUseCase` and update the import to come from `current_account/port.py`. Remove the `provide_all(CurrentAccountHandler)` line from the DI container — Dishka already provides `CurrentAccountHandler` as `CurrentAccountUseCase` via the existing `provide(CurrentAccountHandler, provides=CurrentAccountUseCase)` binding.

**Rationale:** The port already exposes the exact method these handlers need (`get_current_account`). There is no reason to depend on the concrete class. The DI container resolves the same instance either way.

**Alternative considered:** Create a separate domain service for "get current account" logic. Rejected — the existing `CurrentAccountUseCase` port already serves this purpose perfectly.

### Decision 3: Introduce `AuthorizationGuard` port in shared domain

**Choice:** Create `shared/domain/ports/authorization_guard.py` with a Protocol defining `async def require_admin(self) -> None` that raises `AuthorizationError` if the current user lacks admin access. Implement it as `AccountAuthorizationGuard` in `account/infrastructure/security/`. Wire it in the DI container.

**Rationale:** This keeps `IdentityProvider` focused on identity ("who are you?") and separates authorization ("can you do this?") into its own port. Core context can depend on the shared port without knowing anything about Account's domain model. The implementation lives in Account's infrastructure where it has natural access to `AccountRepository` and `AccountRole`.

**Alternative considered:**
- Extending `IdentityProvider` with `require_admin()` — rejected because it mixes identity and authorization concerns.
- Encoding role in the JWT token — rejected because it creates stale authorization data.

## Risks / Trade-offs

- **[Low] Import path churn** → All changes are mechanical find-and-replace operations. Tests importing `register_event` from the old path will need updating, but the infrastructure module can re-export for backward compatibility during transition.
- **[Low] `AuthorizationGuard` is narrow** → It only has `require_admin()` for now. If more granular checks are needed later, the port can be extended. This is intentional — we solve the current violation without over-engineering.
- **[None] Behavioral risk** → No logic changes. Same code runs, same DI resolution, just through abstractions instead of concrete types.
