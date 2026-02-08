## ADDED Requirements

### Requirement: AuthSession aggregate root at domain/auth_session/entity.py
The system SHALL define an `AuthSession` class extending `AggregateRoot` in `domain/auth_session/entity.py`. AuthSession MUST contain fields: `id_` (session ID string), `user_id` (UserId), `expiration` (datetime). AuthSession is a separate aggregate from User — it references User by `UserId` only, never by direct object reference.

#### Scenario: AuthSession references User by ID only
- **WHEN** inspecting AuthSession's fields
- **THEN** it contains `user_id: UserId` and does NOT hold a direct reference to a `User` object

#### Scenario: AuthSession is an AggregateRoot
- **WHEN** an AuthSession instance is created
- **THEN** it supports domain event collection via `_register_event()` and `collect_events()`

### Requirement: AuthSession domain events at domain/auth_session/events.py
The system SHALL define domain events: `SessionCreated`, `SessionExpired`, `SessionRevoked` in `domain/auth_session/events.py`. Each MUST extend `DomainEvent`.

#### Scenario: SessionCreated contains session and user identifiers
- **WHEN** a `SessionCreated` event is emitted
- **THEN** it contains `session_id` and `user_id`

### Requirement: AuthSession gateway port at domain/auth_session/gateway.py
The system SHALL define an `AuthSessionGateway` protocol in `domain/auth_session/gateway.py` with methods for creating, reading, and deleting sessions. This is the driven port for session persistence.

#### Scenario: AuthSessionGateway is a protocol-based port
- **WHEN** an infrastructure adapter implements `AuthSessionGateway`
- **THEN** it satisfies the protocol via structural typing

### Requirement: AuthSession domain errors at domain/auth_session/errors.py
The system SHALL define session-specific errors in `domain/auth_session/errors.py` (e.g., `SessionNotFoundError`, `SessionExpiredError`).

#### Scenario: SessionExpiredError extends DomainError
- **WHEN** a `SessionExpiredError` is raised
- **THEN** it is catchable as `DomainError`
