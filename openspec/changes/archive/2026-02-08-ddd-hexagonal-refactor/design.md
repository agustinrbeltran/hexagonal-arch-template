## Context

The project is a FastAPI-based hexagonal architecture template (`hexagonal-arch-template`) using Python 3.13, SQLAlchemy 2.0, Dishka DI, bcrypt, and PyJWT. It currently organizes code by feature (`src/features/{feature}/domain|adapter|entrypoint`) with shared infrastructure in `src/common/` and bootstrap in `src/setup/`.

The architecture already has many DDD-aligned concepts — entities with identity, value objects (frozen dataclasses), repository interfaces (protocols), inbound/outbound ports — but they are inconsistently placed. Domain services double as application-layer use case handlers, there is no aggregate root abstraction, no domain event support, and the `application/` layer is essentially absent. The `clean-ddd-hexagonal` skill defines a target architecture with strict layer separation (`domain/ → application/ → infrastructure/`), aggregate boundaries, domain events, and clear port/adapter naming.

Two bounded contexts exist today: **User** (CRUD + role management) and **Account** (authentication sessions — sign-up, log-in, log-out, change-password). Database is PostgreSQL with imperative SQLAlchemy mapping. HTTP API contracts (endpoints, request/response shapes) are stable and must not change.

## Goals / Non-Goals

**Goals:**
- Restructure from feature-based layout to layer-first layout (`src/domain/`, `src/application/`, `src/infrastructure/`)
- Introduce proper aggregate root base class with domain event collection
- Separate domain services (pure business rules) from application services (orchestration / use cases)
- Define explicit command/query DTOs for each use case
- Establish a `DomainEvent` base class and aggregate-level `collect_events()` pattern
- Relocate all framework/adapter code into `src/infrastructure/`
- Preserve all existing HTTP API behavior — zero breaking changes to consumers

**Non-Goals:**
- CQRS with separate read/write databases — start simple, evolve later
- Event Sourcing — standard state-based persistence remains
- Message broker / async event publishing — domain events are dispatched in-process only
- New features or business logic changes — this is a structural refactor only
- Database migration or schema changes — tables/columns remain identical

## Decisions

### 1. Layer-first directory layout over feature-first

**Decision**: Top-level directories are `domain/`, `application/`, `infrastructure/` (layers), not `features/{name}` (bounded contexts).

**Rationale**: The skill reference prescribes layer-first with aggregates nested under `domain/{aggregate}/`. The project has only two small bounded contexts (User, Account) — feature-first adds unnecessary nesting. Layer-first makes the dependency rule physically visible via directory structure.

**Alternative considered**: Keep feature-first, add layers within each feature. Rejected because the skill's canonical structure is layer-first, and two features don't justify the indirection.

### 2. Aggregate organization under domain/

**Decision**: Each aggregate gets its own directory under `domain/`:
```
src/domain/
├── shared/          # Base classes, shared errors
├── user/            # User aggregate
│   ├── entity.py
│   ├── value_objects.py
│   ├── events.py
│   ├── repository.py
│   ├── services.py
│   └── errors.py
└── auth_session/    # AuthSession aggregate
    ├── entity.py
    ├── value_objects.py
    ├── events.py
    ├── gateway.py
    └── errors.py
```

**Rationale**: Follows the skill's directory structure exactly. Each aggregate is self-contained with its entities, VOs, events, and repository port.

### 3. Application layer with use-case-per-directory

**Decision**: Each use case gets its own directory under `application/`:
```
src/application/
├── shared/
│   └── unit_of_work.py
├── create_user/
│   ├── command.py
│   ├── handler.py
│   └── port.py
├── sign_up/
│   ├── command.py
│   ├── handler.py
│   └── port.py
└── ...
```

**Rationale**: Aligns with the skill's `application/{use-case}/command|handler|port` convention. Each use case is independently testable. Handlers depend on domain ports (repositories) and the unit-of-work port.

**Alternative considered**: Group use cases by aggregate (e.g., `application/user/create.py`). Rejected because the skill prescribes flat use-case directories, and cross-aggregate use cases (sign-up touches both User and AuthSession) don't fit aggregate grouping.

### 4. Domain events as in-process collection, not external messaging

**Decision**: Aggregates collect `DomainEvent` instances via `_events` list. After the use case handler completes, the unit-of-work adapter dispatches events in-process. No message broker.

**Rationale**: The project doesn't need async event publishing yet. In-process dispatch is the simplest starting point per the skill's complexity ladder (Level 2-3). Events can be promoted to integration events later.

### 5. Keep Dishka as DI framework, relocate providers

**Decision**: All Dishka providers move to `src/infrastructure/config/di/`. Provider modules map to layers: `domain.py`, `application.py`, `infrastructure.py`, `settings.py`.

**Rationale**: Dishka is already deeply integrated and works well. The composition root belongs in infrastructure per the skill's guidance. No reason to switch DI frameworks.

### 6. Infrastructure adapter organization

**Decision**:
```
src/infrastructure/
├── persistence/       # SQLAlchemy repos, mappers, session factories
├── http/              # FastAPI controllers, routers, middleware, DTOs
├── security/          # bcrypt hasher, JWT processor, cookie transport
└── config/
    ├── di/            # Dishka providers (composition root)
    ├── settings/      # Pydantic settings models
    └── app_factory.py # FastAPI app bootstrap
```

**Rationale**: Groups adapters by technology concern, not by feature. REST controllers are driver adapters under `http/`; SQLAlchemy repos are driven adapters under `persistence/`. Security adapters (bcrypt, JWT) get their own directory since they're shared across aggregates.

### 7. Base classes in domain/shared/

**Decision**: Introduce `domain/shared/` with:
- `entity.py` — `Entity[ID]` base (already exists, keep)
- `aggregate_root.py` — `AggregateRoot[ID]` extending Entity, adds `_events` list and `collect_events()`
- `value_object.py` — `ValueObject` base (already exists, keep)
- `domain_event.py` — `DomainEvent` base with `event_id`, `occurred_at`, `event_type`
- `errors.py` — Shared domain errors

**Rationale**: These are the DDD tactical building blocks from the skill. AggregateRoot is the key new abstraction; Entity and ValueObject bases already exist and need only minor adjustment.

## Risks / Trade-offs

- **Large diff / all-at-once migration** → Mitigate by doing this on a dedicated branch (`ddd-refactor`), using tasks to break work into reviewable chunks. Every intermediate commit should keep tests passing.
- **Import path churn** → Every `from src.features.user.domain...` import changes. Mitigate with IDE-assisted refactoring and grep-based verification. Consider a single search-and-replace pass per moved module.
- **Dishka provider rewiring** → Moving provider modules means re-verifying all DI bindings work. Mitigate by running the full test suite after each provider migration step.
- **Two-aggregate system may feel over-structured** → The layer-first + use-case-per-directory layout is heavier than needed for 2 aggregates. Accepted trade-off: this is a template project meant to demonstrate the pattern at scale.
- **No automated architecture tests yet** → After refactor, there's no tooling to enforce the dependency rule. Consider adding `import-linter` or similar in a follow-up change.
