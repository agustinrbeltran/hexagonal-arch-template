## ADDED Requirements

### Requirement: User aggregate root at domain/user/entity.py
The system SHALL define a `User` class extending `AggregateRoot[UserId]` in `domain/user/entity.py`. User MUST be the sole aggregate root for user-related data. It MUST contain fields: `id_` (UserId), `username` (Username), `password_hash` (UserPasswordHash), `role` (UserRole), `is_active` (bool).

#### Scenario: User is an AggregateRoot
- **WHEN** a User instance is created
- **THEN** it is an instance of `AggregateRoot[UserId]` and supports domain event collection

#### Scenario: User identity is UserId
- **WHEN** comparing two User instances
- **THEN** equality is determined by `id_` (UserId), not by username or other attributes

### Requirement: User value objects at domain/user/value_objects.py
The system SHALL define value objects `UserId`, `Username`, `UserPasswordHash`, and `RawPassword` in `domain/user/value_objects.py`. Each MUST be a frozen dataclass extending ValueObject. `Username` MUST validate length (5-20 chars) and character constraints on creation.

#### Scenario: Username validates on creation
- **WHEN** a Username is created with a string shorter than 5 characters
- **THEN** a domain error is raised

#### Scenario: UserId is a value object with UUID
- **WHEN** two UserId instances wrap the same UUID
- **THEN** they are considered equal

### Requirement: User domain events at domain/user/events.py
The system SHALL define domain events in `domain/user/events.py`: `UserCreated`, `UserActivated`, `UserDeactivated`, `UserRoleChanged`, `UserPasswordChanged`. Each event MUST extend `DomainEvent` and include relevant aggregate data.

#### Scenario: UserCreated event contains user data
- **WHEN** a User aggregate emits a `UserCreated` event
- **THEN** the event contains `user_id`, `username`, and `role`

#### Scenario: Events are named in past tense
- **WHEN** inspecting domain event class names in `domain/user/events.py`
- **THEN** all names are past tense (e.g., `UserCreated`, not `CreateUser`)

### Requirement: User repository port at domain/user/repository.py
The system SHALL define a `UserRepository` protocol in `domain/user/repository.py` with methods: `save(user)`, `get_by_id(user_id)`, `get_by_username(username)`, `get_all(pagination, sorting)`. This is a driven port — the interface lives in domain, the implementation in infrastructure.

#### Scenario: UserRepository is a protocol
- **WHEN** an infrastructure adapter implements `UserRepository`
- **THEN** it satisfies the protocol without inheriting from it (structural typing)

### Requirement: User domain services at domain/user/services.py
The system SHALL define stateless domain services in `domain/user/services.py` for logic that spans multiple entities or requires external port dependencies. The `UserService` MUST contain authorization checks and role hierarchy logic.

#### Scenario: Domain service enforces role hierarchy
- **WHEN** a non-admin user attempts to grant admin role
- **THEN** the domain service raises an `AuthorizationError`

### Requirement: User domain errors at domain/user/errors.py
The system SHALL define user-specific domain errors in `domain/user/errors.py` (e.g., `UserNotFoundError`, `UsernameAlreadyExistsError`, `InactiveUserError`).

#### Scenario: UserNotFoundError extends DomainError
- **WHEN** a `UserNotFoundError` is raised
- **THEN** it is catchable as `DomainError`
