## Why

The current codebase follows a feature-based hexagonal architecture (`src/features/{feature}/domain|adapter|entrypoint`) but mixes DDD tactical concerns — domain services double as application use case handlers, the `application/` layer is essentially empty, and there is no clear aggregate boundary or domain event support. Refactoring to a strict Clean Architecture + DDD + Hexagonal structure (as defined in the `clean-ddd-hexagonal` skill) will enforce the dependency rule, separate orchestration from business logic, and make the codebase ready for domain events, CQRS, and multi-aggregate workflows.

## What Changes

- **BREAKING**: Restructure `src/` from `features/{name}/domain|adapter|entrypoint` to `src/domain/`, `src/application/`, `src/infrastructure/`, `src/main.py` top-level layout
- Move pure business logic (entities, value objects, domain services) into `src/domain/{aggregate}/`
- Create proper aggregate roots (`User`, `AuthSession`) with enforced invariants and domain event support
- Introduce `src/application/{use-case}/` with explicit command/handler/port separation — currently domain services act as both domain and application logic
- Relocate all SQLAlchemy adapters, REST controllers, and framework code into `src/infrastructure/`
- Move DI composition root from `src/setup/ioc/` to `src/infrastructure/config/di/`
- Introduce a shared `domain/shared/` module for base classes (Entity, AggregateRoot, ValueObject, DomainEvent)
- Add domain event infrastructure (event collection on aggregates, dispatcher)
- Introduce `application/shared/unit_of_work.py` port for transaction abstraction

## Capabilities

### New Capabilities
- `domain-model`: Base DDD building blocks — Entity, AggregateRoot, ValueObject, DomainEvent base classes; shared domain errors
- `user-aggregate`: User aggregate root with child entities, value objects, domain events, repository port, and domain services
- `auth-session-aggregate`: AuthSession aggregate with value objects, events, gateway port, and session lifecycle logic
- `application-use-cases`: Application-layer use case structure — command/query DTOs, handlers, driver port interfaces, unit of work
- `infrastructure-adapters`: Driven adapters (persistence, messaging) and driver adapters (REST controllers, middleware); DI composition root
- `domain-events`: Domain event base class, aggregate event collection, in-process event dispatcher, integration event mapping

### Modified Capabilities
_(No existing specs to modify — this is a greenfield spec setup)_

## Impact

- **Code**: Every file under `src/` will move or be restructured. Import paths change project-wide.
- **APIs**: No HTTP API contract changes — same endpoints, same request/response shapes.
- **Dependencies**: No new PyPI packages required. Dishka, SQLAlchemy, FastAPI, bcrypt, PyJWT all remain.
- **Database**: No schema changes — same tables, same columns.
- **Tests**: Test imports will need updating to match new module paths. Test structure should mirror the new `domain/application/infrastructure` split.
- **DI**: Dishka provider modules will be reorganized under `src/infrastructure/config/di/`.
