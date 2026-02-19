## MODIFIED Requirements

### Requirement: Entity base class with identity equality
The system SHALL provide an `Entity[ID]` base class in `shared/domain/entity.py` (shared kernel) that compares instances by identity (ID), not by attribute values. The class MUST be generic over the ID type.

#### Scenario: Two entities with same ID are equal
- **WHEN** two Entity instances have the same `id_` value
- **THEN** `entity_a == entity_b` returns True regardless of other attribute differences

### Requirement: AggregateRoot base class extending Entity
The system SHALL provide an `AggregateRoot[ID]` base class in `shared/domain/aggregate_root.py` (shared kernel) that extends `Entity[ID]`. AggregateRoot MUST support collecting domain events via an internal `_events` list.

#### Scenario: AggregateRoot collects domain events
- **WHEN** an aggregate root registers a domain event via `_register_event(event)`
- **THEN** the event is appended to the aggregate's internal `_events` list

### Requirement: ValueObject base class with structural equality
The system SHALL provide a `ValueObject` base class in `shared/domain/value_object.py` (shared kernel). Value objects MUST be immutable (frozen dataclasses) and MUST compare by value (all attributes).

#### Scenario: Two value objects with same attributes are equal
- **WHEN** two ValueObject instances have identical attribute values
- **THEN** they are considered equal

### Requirement: DomainEvent base class
The system SHALL provide a `DomainEvent` base class in `shared/domain/domain_event.py` (shared kernel) with fields: `event_id` (UUID string), `occurred_at` (UTC datetime), and an abstract `event_type` property.

#### Scenario: DomainEvent auto-generates event_id and timestamp
- **WHEN** a new DomainEvent subclass is instantiated
- **THEN** `event_id` is a unique UUID string and `occurred_at` is the current UTC time

### Requirement: Shared domain errors module
The system SHALL provide `shared/domain/errors.py` containing base domain error classes (`DomainError`, `DomainTypeError`, `NotFoundError`, `AuthorizationError`).

#### Scenario: Domain errors are catchable by base type
- **WHEN** a `NotFoundError` is raised in domain logic
- **THEN** it can be caught as a `DomainError`

### Requirement: Domain layer has zero external dependencies
Each bounded context's `domain/` package and the shared kernel's `domain/` package MUST NOT import any framework, ORM, or infrastructure library (SQLAlchemy, FastAPI, Dishka, bcrypt, PyJWT). All domain code MUST be pure Python with stdlib-only imports.

#### Scenario: Domain module imports are clean
- **WHEN** inspecting all imports across `src/**/domain/**/*.py`
- **THEN** no import statement references `sqlalchemy`, `fastapi`, `dishka`, `bcrypt`, or `jwt`

## ADDED Requirements

### Requirement: AccountId in shared kernel
The system SHALL define `AccountId` as a `ValueObject` in `shared/domain/account_id.py`. It SHALL wrap a UUID. This value object is in the shared kernel because it is referenced by both Account BC (as the aggregate ID) and Core BC (as a foreign key in Profile).

#### Scenario: AccountId used across contexts
- **WHEN** both Account BC and Core BC need to reference an account identity
- **THEN** they import `AccountId` from `shared.domain.account_id`

### Requirement: IdentityProvider in shared kernel
The system SHALL define an `IdentityProvider` protocol in `shared/domain/ports/identity_provider.py` with method `get_current_account_id() -> AccountId`. This is in the shared kernel because both contexts need to identify the current authenticated account.

#### Scenario: IdentityProvider returns AccountId
- **WHEN** `get_current_account_id()` is called
- **THEN** it returns an `AccountId` from the JWT token

### Requirement: Permission base types in shared kernel
The system SHALL define `Permission[PC]`, `AnyOf[PC]`, `PermissionContext`, and `authorize()` in `shared/domain/authorization.py`. These are generic authorization primitives used by any bounded context that needs permission checks.

#### Scenario: Permission base types available to contexts
- **WHEN** Account BC defines `CanManageSubordinate`
- **THEN** it extends `Permission` from the shared kernel
