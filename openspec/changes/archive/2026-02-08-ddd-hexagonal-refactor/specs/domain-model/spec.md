## ADDED Requirements

### Requirement: Entity base class with identity equality
The system SHALL provide an `Entity[ID]` base class in `domain/shared/entity.py` that compares instances by identity (ID), not by attribute values. The class MUST be generic over the ID type.

#### Scenario: Two entities with same ID are equal
- **WHEN** two Entity instances have the same `id_` value
- **THEN** `entity_a == entity_b` returns True regardless of other attribute differences

#### Scenario: Two entities with different IDs are not equal
- **WHEN** two Entity instances have different `id_` values
- **THEN** `entity_a == entity_b` returns False

### Requirement: AggregateRoot base class extending Entity
The system SHALL provide an `AggregateRoot[ID]` base class in `domain/shared/aggregate_root.py` that extends `Entity[ID]`. AggregateRoot MUST support collecting domain events via an internal `_events` list.

#### Scenario: AggregateRoot collects domain events
- **WHEN** an aggregate root registers a domain event via `_register_event(event)`
- **THEN** the event is appended to the aggregate's internal `_events` list

#### Scenario: AggregateRoot events can be collected and cleared
- **WHEN** `collect_events()` is called on an aggregate root
- **THEN** all accumulated events are returned and the internal list is cleared

### Requirement: ValueObject base class with structural equality
The system SHALL provide a `ValueObject` base class in `domain/shared/value_object.py`. Value objects MUST be immutable (frozen dataclasses) and MUST compare by value (all attributes).

#### Scenario: Two value objects with same attributes are equal
- **WHEN** two ValueObject instances have identical attribute values
- **THEN** they are considered equal

#### Scenario: Value objects are immutable
- **WHEN** code attempts to modify an attribute of a ValueObject instance
- **THEN** the operation raises an error (FrozenInstanceError)

### Requirement: DomainEvent base class
The system SHALL provide a `DomainEvent` base class in `domain/shared/domain_event.py` with fields: `event_id` (UUID string), `occurred_at` (UTC datetime), and an abstract `event_type` property.

#### Scenario: DomainEvent auto-generates event_id and timestamp
- **WHEN** a new DomainEvent subclass is instantiated
- **THEN** `event_id` is a unique UUID string and `occurred_at` is the current UTC time

### Requirement: Shared domain errors module
The system SHALL provide `domain/shared/errors.py` containing base domain error classes (`DomainError`, `DomainTypeError`, `NotFoundError`, `AuthorizationError`).

#### Scenario: Domain errors are catchable by base type
- **WHEN** a `NotFoundError` is raised in domain logic
- **THEN** it can be caught as a `DomainError`

### Requirement: Domain layer has zero external dependencies
The `domain/` package MUST NOT import any framework, ORM, or infrastructure library (SQLAlchemy, FastAPI, Dishka, bcrypt, PyJWT). All domain code MUST be pure Python with stdlib-only imports.

#### Scenario: Domain module imports are clean
- **WHEN** inspecting all imports across `src/domain/**/*.py`
- **THEN** no import statement references `sqlalchemy`, `fastapi`, `dishka`, `bcrypt`, or `jwt`
