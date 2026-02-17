# Overview

📘 This FastAPI-based project demonstrates a practical implementation of **Domain-Driven Design (DDD)** with **Clean Architecture** using a **layer-based organization**. It showcases DDD tactical patterns including aggregates, domain events, value objects, and the repository pattern, combined with Clean Architecture's dependency rule and CQRS principles. While not meant to serve as a comprehensive reference or a strict application of these methodologies, the project shows how their core ideas can be effectively applied in Python for building maintainable, testable systems with complex business logic. If these patterns are new to you, refer to the [Useful Resources](#useful-resources) section.

This template demonstrates how to organize code around domain aggregates and use cases rather than technical layers, while maintaining clear separation of concerns through the domain, application, and infrastructure layers. See [About This Template](#about-this-template) for the relationship to the original work.

## About This Template

This project demonstrates how to apply Domain-Driven Design tactical patterns in a FastAPI application using Clean Architecture principles. The codebase is organized into three distinct layers (domain, application, infrastructure) with clear boundaries and dependency rules.

**What This Template Provides:**
- Layer-based DDD architecture with explicit aggregate boundaries
- Domain events for recording state changes and enabling eventual consistency
- Rich value objects with embedded validation logic
- Application layer use cases following the Command/Handler pattern
- Repository pattern with domain-defined interfaces and infrastructure implementations
- CQRS separation for optimized read and write operations
- Comprehensive dependency injection using Dishka (framework-agnostic)
- Enhanced developer tooling (comprehensive Makefile, code quality automation)

**Foundation:** This template builds upon the excellent architectural foundation from [fastapi-clean-example](https://github.com/ivan-borovets/fastapi-clean-example) by **Ivan Borovets**, evolving it to emphasize DDD tactical patterns and aggregate-driven design. Credit to Ivan for the foundational work that made this possible.

# Table of contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
   1. [Introduction](#introduction)
   2. [Hexagonal Architecture Approach](#hexagonal-architecture-approach)
   3. [Dependency Rule](#dependency-rule)
      1. [Note on Adapters](#note-on-adapters)
   4. [Hexagonal Architecture Continued](#hexagonal-architecture-continued)
   5. [Dependency Inversion](#dependency-inversion)
   6. [Dependency Injection](#dependency-injection)
   7. [CQRS](#cqrs)
3. [Project](#project)
   1. [Dependency Graphs](#dependency-graphs)
   2. [Structure](#structure)
   3. [Makefile Commands Reference](#makefile-commands-reference)
   4. [Technology Stack](#technology-stack)
   5. [API](#api)
      1. [General](#general)
      2. [Account](#account-apiv1account)
      3. [Users](#users-apiv1users)
   6. [Configuration](#configuration)
      1. [Files](#files)
      2. [Flow](#flow)
      3. [Local Environment](#local-environment)
      4. [Other Environments](#other-environments-devprod)
      5. [Adding New Environments](#adding-new-environments)
4. [Useful Resources](#useful-resources)
5. [Support the Project](#-support-the-project)
6. [Acknowledgements](#acknowledgements)

# Architecture Principles

## Introduction

This repository may be helpful for those seeking backend implementation in
Python that is both framework-agnostic and storage-agnostic (unlike Django).
Such flexibility can be achieved by using a web framework that doesn't impose
strict software design (like FastAPI) and applying a layered architecture
patterned after the one proposed by Robert Martin, which we'll explore further.

The original explanation of Clean Architecture concepts can be found
[here](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).
If you're still wondering why Clean Architecture matters, read the article — it
only takes about 5 minutes. In essence, it’s about making your application
independent of external systems and highly testable.

<p align="center">
  <img src="docs/Robert_Martin_CA.png" alt="Clean Architecture Diagram" />
  <br><em>Figure 1: <b>Robert Martin's</b> Clean Architecture Diagram</em>
</p>

> "A computer program is a detailed description of the **policy** by which
> inputs are transformed into outputs."
>
> — Robert Martin

The most abstract policies define core business rules, while the least abstract
ones handle I/O operations. Being closer to implementation details, less
abstract policies are more likely to change. **Layer** represents a collection
of components expressing policies at the same level of abstraction.

Concentric circles represent boundaries between different layers. The meaning of
arrows in the diagram will be discussed [later](#dependency-rule). For now, we
will focus on the purpose of the layers.

## Layer-Based DDD Architecture

This project implements **Domain-Driven Design** tactical patterns using **Clean Architecture's** layered approach. Code is organized into three distinct layers (domain, application, infrastructure), with business logic concentrated in domain **aggregates** that represent bounded contexts.

### The Three Layers

The architecture follows a strict layering principle where dependencies flow inward:

```
Infrastructure → Application → Domain
   (adapters)     (use cases)    (core)
```

Each layer has specific responsibilities and constraints:

![#gold](https://placehold.co/15x15/gold/gold.svg) **Domain Layer** (`src/domain/`)

The **domain layer** contains pure business logic with **zero external dependencies**. It is organized into **aggregates**, each representing a bounded context with its own model and rules.

**Aggregates in this project:**
- `domain/user/` — User identity, roles, and lifecycle management
- `domain/shared/` — Common domain building blocks (base classes, shared exceptions)

> **Note:** Authentication (JWT access tokens and refresh tokens) is handled entirely in the infrastructure layer — it is not a domain concern. The domain layer contains only the `User` aggregate.

**What belongs in the domain layer:**

✓ **Aggregate Roots** — Entities that serve as entry points to aggregates. They enforce invariants and emit domain events.
  - Example: `User` entity in `domain/user/entity.py`
  - Extends `AggregateRoot` base class
  - Manages its own lifecycle and state changes

✓ **Value Objects** — Immutable types defined by their attributes, not identity. They contain validation logic.
  - Examples: `UserId`, `Username`, `UserPasswordHash`, `RawPassword`
  - Found in `domain/user/value_objects.py`
  - Equality by value, not reference

✓ **Domain Events** — Immutable records of state changes that have occurred.
  - Examples: `UserCreated`, `UserActivated`, `UserRoleChanged`
  - Found in `domain/user/events.py`
  - Past-tense naming, frozen dataclasses

✓ **Repository Interfaces** — Abstractions for aggregate persistence (ports).
  - Example: `UserRepository` protocol in `domain/user/repository.py`
  - Defines methods like `get_by_id()`, `save()`, `delete()`
  - Implementation lives in infrastructure layer

✓ **Domain Services** — Stateless operations that don't naturally fit in entities.
  - Example: `UserService` in `domain/user/services.py`
  - Coordinates operations across value objects and entities
  - May verify business rules or prepare data

✓ **Domain Exceptions** — Business rule violations.
  - Example: `UserNotFoundError`, `RoleAssignmentNotPermittedError`
  - Found in `domain/user/errors.py`

**What does NOT belong in the domain layer:**

✗ Database code (SQLAlchemy models, queries)
✗ HTTP/REST code (FastAPI routes, request models)
✗ Framework dependencies (except language extensions)
✗ External API calls
✗ File I/O operations

**Example - User Aggregate:**

```python
class User(AggregateRoot[UserId]):
    """
    User aggregate root - manages user identity and lifecycle.

    Invariants enforced:
    - Super admin cannot be deactivated
    - Only assignable roles can be granted
    - Username must be unique (via repository)
    """

    def change_role(self, new_role: UserRole) -> None:
        """Change user role and emit domain event."""
        if not new_role.is_assignable:
            raise RoleAssignmentNotPermittedError(new_role)

        old_role = self.role
        self.role = new_role

        # Record domain event
        self.record_event(UserRoleChanged(
            user_id=self.id_.value,
            old_role=old_role,
            new_role=new_role,
        ))
```

**Aggregate Boundaries:**

Aggregates define transactional consistency boundaries. Changes within an aggregate are atomic, while changes across aggregates are eventually consistent through domain events.

```
┌─────────────────────────────────────────┐
│            User Aggregate               │
│  (domain/user/)                         │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  User (Root)                     │  │
│  │  • id: UserId                    │  │
│  │  • username: Username            │  │
│  │  • password_hash: PasswordHash   │  │
│  │  • role: UserRole                │  │
│  │  • is_active: bool               │  │
│  └──────────────────────────────────┘  │
│                                         │
│  Invariants:                            │
│  • Role assignment rules                │
│  • Activation constraints               │
│  • Password complexity                  │
└─────────────────────────────────────────┘

```

Note: In projects with multiple aggregates, they reference each other **by ID only**, never by embedding. This maintains clear boundaries and supports eventual consistency.

![#purple](https://placehold.co/15x15/purple/purple.svg) **Application Layer** (`src/application/`)

The **application layer** orchestrates use cases by coordinating domain objects and infrastructure. It depends on the domain layer but has no knowledge of specific infrastructure implementations.

**What belongs in the application layer:**

✓ **Use Case Handlers** — Implement business workflows by orchestrating domain logic.
  - Example: `LogInHandler` in `application/log_in/handler.py`
  - Loads aggregates from repositories
  - Invokes domain services
  - Persists changes
  - Dispatches domain events

✓ **Command DTOs** — Plain data structures carrying request data.
  - Example: `LogInCommand` in `application/log_in/command.py`
  - Immutable, frozen dataclasses
  - No business logic, just data transfer

✓ **Use Case Ports** — Interfaces that handlers implement.
  - Example: `LogInUseCase` protocol in `application/log_in/port.py`
  - Controllers depend on these abstractions
  - Enables testing with different implementations

✓ **Transaction Boundaries** — Unit of Work pattern for atomic operations.
  - Found in `application/shared/unit_of_work.py`
  - Ensures all-or-nothing persistence

**Application layer responsibilities:**
1. Validate commands (structure, not business rules)
2. Load aggregates from repositories
3. Invoke domain logic (entities, services)
4. Persist changes (through repositories)
5. Dispatch domain events
6. Handle application-level errors

**Example - Log In Use Case:**

```python
class LogInHandler(LogInUseCase):
    """
    Handles user authentication and issues JWT token pair.

    Flow:
    1. Load user aggregate by username
    2. Verify password (domain service)
    3. Check if user is active
    4. Issue access + refresh token pair (infrastructure)
    5. Return tokens
    """

    def __init__(
        self,
        user_repository: UserRepository,       # Domain port
        user_service: UserService,              # Domain service
        token_pair_issuer: TokenPairIssuer,     # Application port
    ) -> None:
        self._user_repository = user_repository
        self._user_service = user_service
        self._token_pair_issuer = token_pair_issuer

    async def execute(self, command: LogInCommand) -> LogInResult:
        # Load aggregate (domain)
        user = await self._user_repository.get_by_username(
            Username(command.username)
        )

        # Verify password (domain logic)
        if not await self._user_service.is_password_valid(
            user, RawPassword(command.password)
        ):
            raise AuthenticationError("Invalid password")

        # Check business rule (domain)
        if not user.is_active:
            raise AuthenticationError("Account inactive")

        # Issue JWT access token + refresh token (infrastructure)
        access_token, refresh_token = (
            self._token_pair_issuer.issue_token_pair(user.id_)
        )

        return LogInResult(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._token_pair_issuer.access_token_expiry_seconds,
        )
```

**Key principle:** Application handlers orchestrate but never contain business logic. All business rules live in the domain layer.

![#green](https://placehold.co/15x15/green/green.svg) **Infrastructure Layer** (`src/infrastructure/`)

The **infrastructure layer** provides concrete implementations of domain and application ports. It contains all framework-specific code and external system integrations.

**What belongs in the infrastructure layer:**

✓ **Repository Implementations** — Concrete persistence adapters.
  - Example: `SqlaUserRepository` in `infrastructure/persistence/`
  - Implements `UserRepository` domain port
  - Uses SQLAlchemy for database access
  - Translates between domain entities and ORM models

✓ **HTTP Controllers** — REST API endpoints.
  - Example: Controllers in `infrastructure/http/controllers/`
  - Validate HTTP request structure
  - Invoke application use cases
  - Format HTTP responses
  - Translate domain errors to HTTP status codes

✓ **Security Implementations** — Concrete security adapters.
  - Example: `BcryptPasswordHasher` in `infrastructure/security/`
  - Implements password hashing domain port (bcrypt + HMAC pepper)
  - `JwtAccessTokenProcessor` — JWT encoding/decoding
  - `RefreshTokenService` — Implements `TokenPairIssuer` and `TokenPairRefresher` ports
  - `JwtBearerIdentityProvider` — Extracts user identity from Bearer tokens

✓ **Event Dispatchers** — Publish domain events to handlers.
  - Example: Event dispatcher in `infrastructure/events/`
  - Collects events from aggregates after persistence
  - Dispatches to registered handlers

✓ **Configuration** — Settings and dependency injection.
  - Found in `infrastructure/config/`
  - Dishka DI container setup
  - Environment-based configuration

**Example - Repository Implementation:**

```python
class SqlaUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository domain port."""

    def __init__(self, session: AsyncSession, mapper: UserMapper):
        self._session = session
        self._mapper = mapper

    async def get_by_username(self, username: Username) -> User:
        stmt = select(UserModel).where(
            UserModel.username == username.value
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise UserNotFoundByUsernameError(username)

        # Translate ORM model to domain entity
        return self._mapper.to_entity(model)

    async def save(self, user: User) -> None:
        # Translate domain entity to ORM model
        model = self._mapper.to_model(user)
        await self._session.merge(model)
```

**Example - HTTP Controller:**

```python
# infrastructure/http/controllers/account/log_in.py
@router.post(
    "/login",
    error_map={
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        UserNotFoundByUsernameError: status.HTTP_404_NOT_FOUND,
    },
    response_model=TokenResponse,
)
@inject
async def login(
    request_data: LogInCommand,
    handler: FromDishka[LogInUseCase],   # Application port
) -> TokenResponse:
    result = await handler.execute(request_data)
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )
```

> [!IMPORTANT]
>
> - The domain layer has **zero dependencies** on application or infrastructure
> - The application layer depends on domain ports (abstractions), never on infrastructure
> - The infrastructure layer implements both domain and application ports
> - This creates testable boundaries: domain can be tested in isolation, application can be tested with in-memory implementations

## DDD Tactical Patterns Deep Dive

This section provides a consolidated reference for all Domain-Driven Design tactical patterns used in this project. Each pattern is explained with real code examples from the codebase.

### Aggregates

An **aggregate** is a cluster of domain objects (entities and value objects) treated as a single unit for data changes. Each aggregate has an **aggregate root** — the only entity externally accessible.

**Key principles:**
- Only the aggregate root can be obtained directly from a repository
- External objects can only reference the aggregate root by identity (ID)
- Aggregates define transactional consistency boundaries
- Changes within an aggregate are atomic; changes across aggregates are eventually consistent

**Aggregates in this project:**

```
User Aggregate (domain/user/)
├── Root: User entity
├── Value Objects: UserId, Username, UserPasswordHash
├── Domain Events: UserCreated, UserActivated, UserRoleChanged
└── Consistency Rules:
    • Username uniqueness
    • Role assignment validation
    • Activation constraints
```

```python
# domain/user/entity.py
class User(AggregateRoot[UserId]):
    """
    User aggregate root.

    Manages user identity, roles, and lifecycle.
    Enforces invariants and emits domain events.
    """

    def __init__(
        self,
        *,
        id_: UserId,
        username: Username,
        password_hash: UserPasswordHash,
        role: UserRole,
        is_active: bool,
    ) -> None:
        super().__init__(id_=id_)
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active

    def activate(self) -> None:
        """Activate a deactivated user."""
        if self.is_active:
            return  # Already active, idempotent

        self.is_active = True
        self.record_event(UserActivated(user_id=self.id_.value))

    def deactivate(self) -> None:
        """Deactivate an active user."""
        if not self.role.can_be_deactivated:
            raise ActivationChangeNotPermittedError(
                "Super admin cannot be deactivated"
            )

        if not self.is_active:
            return  # Already inactive, idempotent

        self.is_active = False
        self.record_event(UserDeactivated(user_id=self.id_.value))
```

**Why aggregates matter:**
- Prevent invariant violations (e.g., super admin deactivation)
- Define clear transaction boundaries
- Enable domain events for eventual consistency
- Simplify testing (test aggregate behavior in isolation)

### Domain Events

**Domain events** are immutable records of something that happened in the domain. They enable loose coupling between aggregates and support eventual consistency.

**Characteristics:**
- Past-tense naming (UserCreated, not CreateUser)
- Immutable (frozen dataclass)
- Contain only necessary data (no objects, just primitives/enums)
- Emitted by aggregate roots

**Events in this project:**

```python
# domain/user/events.py
@dataclass(frozen=True, kw_only=True)
class UserCreated(DomainEvent):
    """Emitted when a new user is created."""
    user_id: UUID
    username: str
    role: UserRole


@dataclass(frozen=True, kw_only=True)
class UserActivated(DomainEvent):
    """Emitted when a deactivated user is reactivated."""
    user_id: UUID


@dataclass(frozen=True, kw_only=True)
class UserRoleChanged(DomainEvent):
    """Emitted when a user's role changes."""
    user_id: UUID
    old_role: UserRole
    new_role: UserRole
```

**Event flow:**

```
1. Aggregate root performs action
   └─> User.change_role(UserRole.ADMIN)

2. Aggregate records event internally
   └─> self.record_event(UserRoleChanged(...))

3. Repository persists aggregate
   └─> await user_repository.save(user)

4. Repository collects and dispatches events
   └─> for event in user.collect_events():
           await event_dispatcher.dispatch(event)

5. Event handlers react
   └─> logger.info(f"User {event.user_id} role changed")
   └─> await cache_invalidator.invalidate_user(event.user_id)
   └─> await notification_service.notify_admin(event)
```

**Use cases for domain events:**
- Audit logging (record all state changes)
- Cache invalidation (when user changes, invalidate cache)
- Notifications (send email when user activated)
- Analytics (track user behavior)
- Eventual consistency across aggregates

### Value Objects

**Value objects** are immutable types defined by their attributes, not identity. They encapsulate validation logic and domain concepts.

**Characteristics:**
- Immutable (frozen dataclass)
- Equality by value, not reference
- Self-validating (validation in `__post_init__`)
- Can have methods (not just data containers)

**Value objects in this project:**

```python
# domain/user/value_objects.py
@dataclass(frozen=True, kw_only=True, slots=True)
class Username(ValueObject):
    """
    Username value object.

    Rules:
    - 3-32 characters
    - Only alphanumeric and underscore
    - Case-insensitive equality
    """
    value: str

    def __post_init__(self) -> None:
        if not 3 <= len(self.value) <= 32:
            raise InvalidUsernameError(
                f"Username must be 3-32 characters, got {len(self.value)}"
            )
        if not self.value.replace("_", "").isalnum():
            raise InvalidUsernameError(
                "Username must be alphanumeric with optional underscores"
            )

    def __eq__(self, other: object) -> bool:
        """Case-insensitive equality."""
        if not isinstance(other, Username):
            return False
        return self.value.lower() == other.value.lower()


@dataclass(frozen=True, kw_only=True, slots=True)
class RawPassword(ValueObject):
    """
    Raw (unhashed) password value object.

    Rules:
    - Minimum 8 characters
    - Maximum 128 characters
    - Must not be empty
    """
    value: str

    def __post_init__(self) -> None:
        if not 8 <= len(self.value) <= 128:
            raise InvalidPasswordError(
                "Password must be 8-128 characters"
            )
```

**Benefits:**
- Type safety (can't pass string where Username expected)
- Encapsulated validation (can't create invalid username)
- Self-documenting (method signature shows intent)
- Reusable (use Username across domain)

### Repository Pattern

**Repositories** provide collection-like access to aggregates, abstracting persistence details.

**Key principles:**
- One repository per aggregate (not per table!)
- Interface defined in domain, implementation in infrastructure
- Returns domain entities, not ORM models
- Only aggregate roots have repositories

**Repository in this project:**

```python
# domain/user/repository.py (PORT - Interface)
class UserRepository(Protocol):
    """
    Repository port for User aggregate.

    Defines persistence operations without
    specifying implementation details.
    """

    async def get_by_id(self, user_id: UserId) -> User:
        """Get user by ID. Raises UserNotFoundError if not found."""
        ...

    async def get_by_username(self, username: Username) -> User:
        """Get user by username. Raises UserNotFoundByUsernameError if not found."""
        ...

    async def save(self, user: User) -> None:
        """Persist user. Create if new, update if exists."""
        ...

    async def delete(self, user_id: UserId) -> None:
        """Delete user by ID."""
        ...


# infrastructure/persistence/repositories/user_repository.py (ADAPTER - Implementation)
class SqlaUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(
        self,
        session: AsyncSession,
        mapper: UserMapper,
    ):
        self._session = session
        self._mapper = mapper

    async def get_by_username(self, username: Username) -> User:
        stmt = select(UserModel).where(
            UserModel.username == username.value
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise UserNotFoundByUsernameError(username)

        # Translate ORM model to domain entity
        return self._mapper.to_entity(model)

    async def save(self, user: User) -> None:
        # Translate domain entity to ORM model
        model = self._mapper.to_model(user)
        await self._session.merge(model)
```

**Why repositories matter:**
- Domain doesn't know about databases, ORMs, SQL
- Easy to test (swap with in-memory implementation)
- Easy to replace (swap PostgreSQL for MongoDB)
- Enforces aggregate boundaries (no cross-aggregate joins)

### Domain Services

**Domain services** contain stateless business logic that doesn't naturally fit in an entity or value object.

**When to use domain services:**
- Logic involves multiple entities or aggregates
- Operation is stateless and doesn't belong to one entity
- Computation depends on external domain concepts

**Domain services in this project:**

```python
# domain/user/services.py
class UserService:
    """
    Domain service for user operations.

    Contains business logic that doesn't naturally
    belong to the User entity or value objects.
    """

    def __init__(
        self,
        user_id_generator: UserIdGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher

    async def create(
        self,
        username: Username,
        raw_password: RawPassword,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        """Create a new User aggregate with hashed password."""
        user_id = self._user_id_generator.generate()
        password_hash = await self._password_hasher.hash(raw_password)
        return User.create(
            id_=user_id,
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )

    async def is_password_valid(
        self,
        user: User,
        raw_password: RawPassword,
    ) -> bool:
        """Verify password against stored hash."""
        return await self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=user.password_hash,
        )

    async def change_password(
        self,
        user: User,
        raw_password: RawPassword,
    ) -> None:
        """Hash new password and update user aggregate."""
        new_hash = await self._password_hasher.hash(raw_password)
        user.change_password(new_hash)
```

**Domain service vs Entity method:**

| Put in Entity | Put in Domain Service |
|---------------|----------------------|
| Single entity operation | Multi-entity coordination |
| Internal state change | External dependencies |
| Entity lifecycle (create, activate) | Stateless computation |
| Enforcing invariants | Cross-aggregate logic |

### Application Services (Use Case Handlers)

**Application services** (handlers) orchestrate use cases by coordinating domain objects and infrastructure.

**Responsibilities:**
- Load aggregates from repositories
- Invoke domain services
- Coordinate multiple aggregates
- Manage transactions (Unit of Work)
- Dispatch domain events

**Handler in this project:**

```python
# application/create_user/handler.py
class CreateUserHandler(CreateUserUseCase):
    """
    Application service for creating users.

    Orchestrates domain and infrastructure
    without containing business logic.
    """

    def __init__(
        self,
        current_user_handler: CurrentUserHandler,
        user_service: UserService,                 # Domain service
        user_repository: UserRepository,           # Domain port
        unit_of_work: UnitOfWork,                  # Application port
        event_dispatcher: EventDispatcher,         # Application port
    ) -> None:
        self._current_user_handler = current_user_handler
        self._user_service = user_service
        self._user_repository = user_repository
        self._unit_of_work = unit_of_work
        self._event_dispatcher = event_dispatcher

    async def execute(self, command: CreateUserCommand) -> CreateUserResponse:
        # 1. Get current user (authorization context)
        current_user = await self._current_user_handler.get_current_user()

        # 2. Authorize (domain permission framework)
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=command.role,
            ),
        )

        # 3. Create aggregate via domain service (hashes password)
        user = await self._user_service.create(
            Username(command.username),
            RawPassword(command.password),
            command.role,
        )

        # 4. Persist (infrastructure)
        self._user_repository.save(user)
        await self._unit_of_work.commit()

        # 5. Dispatch domain events
        await self._event_dispatcher.dispatch(user.collect_events())

        return CreateUserResponse(id=user.id_.value)
```

**Application service vs Domain service:**

| Application Service | Domain Service |
|---------------------|----------------|
| Orchestrates workflow | Pure business logic |
| Coordinates multiple services | Stateless computation |
| Manages transactions | No transaction concerns |
| Can be async (I/O) | Typically sync |
| Lives in `application/` | Lives in `domain/` |

### Command/Handler Pattern

Commands are immutable DTOs carrying request data. Handlers implement use cases.

```python
# application/log_in/command.py
@dataclass(frozen=True, slots=True, kw_only=True)
class LogInCommand:
    username: str
    password: str

@dataclass(frozen=True, slots=True, kw_only=True)
class LogInResult:
    access_token: str
    refresh_token: str
    expires_in: int


# application/log_in/port.py
class LogInUseCase(ABC):
    @abstractmethod
    async def execute(self, command: LogInCommand) -> LogInResult: ...


# application/log_in/handler.py
class LogInHandler(LogInUseCase):
    """Handler implementing the log in use case."""
    async def execute(self, command: LogInCommand) -> LogInResult:
        # Implementation details
        ...
```

**Benefits:**
- Clear separation of input (command) and logic (handler)
- Easy to test (commands are just data)
- Can add middleware (validation, logging, metrics)
- Commands can be queued, replayed, audited

### When to Use Which Pattern

```
┌─────────────────────────────────────────────────────────┐
│ Decision Tree: Where Does This Code Belong?            │
└─────────────────────────────────────────────────────────┘

Is it pure business logic with no I/O?
├─ Yes → DOMAIN LAYER
│  │
│  ├─ Does it have identity and lifecycle?
│  │  ├─ Yes → ENTITY (User)
│  │  └─ No → VALUE OBJECT (Username, UserId)
│  │
│  ├─ Does it record something that happened?
│  │  └─ Yes → DOMAIN EVENT (UserCreated)
│  │
│  ├─ Does it define persistence operations?
│  │  └─ Yes → REPOSITORY INTERFACE (UserRepository)
│  │
│  └─ Is it stateless logic involving multiple entities?
│     └─ Yes → DOMAIN SERVICE (UserService)
│
└─ No → Does it orchestrate domain + infrastructure?
   ├─ Yes → APPLICATION LAYER
   │  └─ APPLICATION SERVICE (CreateUserHandler)
   │
   └─ No → Is it a technical detail?
      └─ Yes → INFRASTRUCTURE LAYER
         ├─ Database → REPOSITORY IMPLEMENTATION
         ├─ HTTP → CONTROLLER
         ├─ Events → EVENT DISPATCHER
         └─ Security → PASSWORD HASHER
```

## Dependency Rule

A dependency occurs when one software component relies on another to operate. If
you were to split all blocks of code into separate modules, dependencies would
manifest as imports between those modules. Typically, dependencies are
graphically depicted in UML style in such a way that

> [!IMPORTANT]
>
> - `A -> B` (**A points to B**) means **A depends on B**.

The key principle of Clean Architecture is the **Dependency Rule**. This rule
states that **more abstract software components must not depend on more concrete
ones.** In other words, dependencies must never point outwards.

> [!IMPORTANT]
>
> - The **domain core** (inside the hexagon) may import external tools and libraries to the
>   extent necessary for describing business logic - those that extend the
>   programming language's capabilities (math/numeric utilities, time zone
>   conversion, object modeling, etc.). This trades some core stability for
>   clarity and expressiveness. What is not acceptable are dependencies that
>   bind business logic to implementation details (including frameworks) or to
>   out-of-process systems (databases, brokers, file systems, cloud SDKs, etc.).
> - Components within the same zone **can depend on each other.** For example,
>   adapters in a feature can interact with one another, and domain services
>   within a feature can call each other.
> - **Entrypoints** (driving adapters) can depend on domain core through **inbound ports**.
>   **Infrastructure adapters** (driven adapters) implement **outbound ports** defined by
>   the domain. Both types of adapters can access domain entities and value objects as needed.
> - Avoid letting business logic leak into adapters. Adapters should focus purely on
>   technical concerns (database queries, API calls, serialization) without containing
>   business rules. However, in specific cases where database constraints enforce business
>   rules, adapters may raise domain-specific exceptions, such as
>   `UsernameAlreadyExistsError` for a `UNIQUE CONSTRAINT` violation. Handling
>   these exceptions in domain services ensures that any business logic
>   expressed in adapters remains under domain control.
> - Avoid introducing elements in the domain core that specifically exist to
>   support adapters. For example, don't add ports or domain logic solely
>   to accommodate a specific infrastructure technology. At first glance, based on
>   imports, it might seem that the Dependency Rule isn't violated. However,
>   you've broken the core idea of the rule by embedding infrastructure concerns
>   (more concrete) into the business logic (more abstract).
> - Each feature's hexagon should be **self-contained**. Cross-feature dependencies
>   should be minimized and go through well-defined integration points. Shared
>   concerns live in `/common`.

### Note on Adapters in Hexagonal Architecture

Hexagonal Architecture distinguishes between two types of adapters:

**Driving Adapters (Primary)** — Initiate interactions with the domain:
- **Entrypoints** such as REST controllers, CLI handlers, message consumers
- These adapters **drive** the application by invoking inbound ports (use cases)
- They translate external requests into domain operations
- Example: `infrastructure/http/controllers/account/log_in.py`

**Driven Adapters (Secondary)** — Provide infrastructure services to the domain:
- **Infrastructure adapters** such as database repositories, external API clients
- These adapters are **driven by** the domain through outbound ports
- They translate domain abstractions into concrete infrastructure operations
- Example: `infrastructure/persistence/sqla_user_repository.py`

Both adapter types depend on the domain through **ports** (abstractions). This creates a dependency structure where:
- Entrypoints depend on **inbound ports** (use case interfaces)
- Infrastructure adapters implement **outbound ports** (gateway interfaces)
- Domain core depends on nothing but port abstractions

This approach is a **pragmatic adaptation** that:
- Avoids excessive abstractions with implementations outside the application's boundaries
- Retains all key advantages of Clean Architecture (testability, replaceability, independence)
- Allows adapters to be removed/replaced along with external systems they connect to
- Simplifies real-world development without compromising architectural principles

The key principle for this project:

> "Dependencies must never point outwards **within the domain core**."

The domain core (entities, value objects, domain services, ports) has zero dependencies on adapters or external systems. Adapters depend on ports, not the other way around.

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 10px; justify-items: center;">
  <img src="docs/onion_1.svg" alt="Revised Interpretation of CA-D" style="width: 400px; height: auto;" />
  <img src="docs/onion_2.svg" alt="Revised Interpretation of CA-D, alternative" style="width: 400px; height: auto;" />
</div>
<p align="center" style="font-size: 14px;">
  <em>Figure 2: <b>Revised Interpretation</b> of Clean Architecture<br>
  (diagrammed — original and alternative representation)
  </em>
</p>

## Hexagonal Architecture Continued

![#blue](https://placehold.co/15x15/blue/blue.svg) **Entrypoints** (`infrastructure/http/controllers/`)

Entrypoints are **driving adapters** that receive external requests and invoke the domain through inbound ports:

- This includes **controllers** (REST, GraphQL, CLI, message consumers, scheduled jobs)
  that translate external requests into domain use case invocations
- Controllers validate inputs and invoke **inbound ports** (use case interfaces)
- The domain core assumes that request data is already validated by controllers,
  allowing it to focus solely on business logic
- Controllers must be as thin as possible, containing no logic beyond basic
  input validation and routing. They act as an intermediary between
  external actors and the domain's inbound ports

**Example Flow:**
1. HTTP request arrives at `POST /api/v1/account/login`
2. Controller (`infrastructure/http/controllers/account/log_in.py`) validates request structure
3. Controller invokes `LogInUseCase` (inbound port) with validated data
4. Handler (`application/log_in/handler.py`) orchestrates the use case
5. Handler calls domain services and outbound ports (`UserRepository`, `TokenPairIssuer`) as needed
6. Infrastructure implements outbound ports, executing database queries and JWT encoding
7. Controller receives result and formats HTTP response

> [!IMPORTANT]
>
> - **_Basic_** validation, like checking whether the structure of the incoming
>   request matches the structure of the defined request model (e.g., type
>   safety and required fields) should be performed by controllers at the
>   entrypoint, while **_business rule_** validation (e.g., ensuring the email domain
>   is allowed, verifying the uniqueness of username, or checking if a user
>   meets the required age) belongs to the Domain core.
> - Business rule validation often involves relationships between fields, such
>   as ensuring that a discount applies only within a specific date range or a
>   promotion code is valid for orders above a certain total.
> - **Carefully** consider using Pydantic for business rule validation. While
>   convenient, Pydantic models are slower than regular dataclasses and reduce
>   domain core stability by coupling business logic to an external library.
> - If you choose Pydantic (or a similar tool bundled with web framework) for
>   domain model definitions, ensure that a Pydantic model in the domain core
>   is a separate model from the one in the entrypoint, even if their
>   structure appears identical. Mixing data presentation logic with business
>   logic is a common mistake made early in development to save effort on
>   creating separate models and field mapping, often due to not understanding
>   that structural similarities are temporary.
> - In hexagonal architecture, controllers depend on **inbound port abstractions**,
>   not directly on domain services. This decoupling allows the same domain logic
>   to be accessed through different entrypoints (REST, GraphQL, CLI) without
>   changing the domain.

![#gray](https://placehold.co/15x15/gray/gray.svg) **External Systems**

External systems operate completely outside the hexagon's boundaries:

- These include web frameworks (FastAPI), databases (PostgreSQL), message brokers,
  third-party APIs, file systems, and other infrastructure components
- External systems have no direct access to the domain core
- They interact with the application only through adapters:
  - **Driving side**: Web frameworks invoke controllers (entrypoints)
  - **Driven side**: Adapters use infrastructure libraries to implement outbound ports
- Because the domain depends only on port abstractions (not concrete implementations),
  external systems can be replaced without affecting business logic
- Examples of replaceability:
  - Switch from PostgreSQL to MongoDB by implementing new adapter
  - Add GraphQL alongside REST by creating new entrypoints
  - Replace bcrypt with Argon2 by swapping `PasswordHasher` implementation

> [!NOTE]
> The hexagon (domain core + ports) is the **stable center** of each feature.
> Everything outside — entrypoints, adapters, and external systems — is **replaceable**
> and depends on the hexagon through abstractions. This is the core value of
> Hexagonal Architecture: protecting business logic from infrastructure volatility.

<p align="center">
  <img src="docs/dep_graph_basic.svg" alt="Basic Dependency Graph" />
  <br><em>Figure 3: Basic Dependency Graph</em>
</p>

## Request Flow Example

Let's trace a complete request through all three layers to see how they interact. We'll follow a user login request from HTTP to database and back.

### HTTP POST /api/v1/account/login

```
┌─────────────────────────────────────────────────────────────┐
│  1. INFRASTRUCTURE LAYER - HTTP Controller                  │
│     infrastructure/http/controllers/account/log_in.py       │
└─────────────────────────────────────────────────────────────┘
         │
         │  Validates HTTP request structure
         │  Passes LogInCommand to use case
         │  Maps errors to HTTP status codes
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  2. APPLICATION LAYER - Use Case Handler                    │
│     application/log_in/handler.py                           │
└─────────────────────────────────────────────────────────────┘
         │
         │  Loads User aggregate from repository
         │  Invokes domain service (password verification)
         │  Checks user activation status
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  3. DOMAIN LAYER - Domain Services & Entities               │
│     domain/user/services.py                                 │
└─────────────────────────────────────────────────────────────┘
         │
         │  Verifies password via PasswordHasher port
         │  Returns validation result
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  4. INFRASTRUCTURE LAYER - Token Issuance                   │
│     infrastructure/security/refresh_token_service.py        │
└─────────────────────────────────────────────────────────────┘
         │
         │  Creates JWT access token (short-lived, stateless)
         │  Creates refresh token (long-lived, stored in DB)
         │  Returns token pair to handler
         │
         ▼
     TokenResponse (access_token + refresh_token + expires_in)
```

### Detailed Flow with Code

**Step 1: HTTP Controller (Infrastructure)**

```python
# infrastructure/http/controllers/account/log_in.py
@router.post(
    "/login",
    error_map={
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        UserNotFoundByUsernameError: status.HTTP_404_NOT_FOUND,
    },
    response_model=TokenResponse,
)
@inject
async def login(
    request_data: LogInCommand,
    handler: FromDishka[LogInUseCase],   # Injected use case port
) -> TokenResponse:
    result = await handler.execute(request_data)
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )
```

**Step 2: Application Handler (Application)**

```python
# application/log_in/handler.py
class LogInHandler(LogInUseCase):
    def __init__(
        self,
        user_repository: UserRepository,       # Domain port
        user_service: UserService,              # Domain service
        token_pair_issuer: TokenPairIssuer,     # Application port
    ) -> None:
        self._user_repository = user_repository
        self._user_service = user_service
        self._token_pair_issuer = token_pair_issuer

    async def execute(self, command: LogInCommand) -> LogInResult:
        # 1. Load aggregate (from repository)
        user = await self._user_repository.get_by_username(
            Username(command.username)
        )

        # 2. Verify password (domain service)
        if not await self._user_service.is_password_valid(
            user, RawPassword(command.password)
        ):
            raise AuthenticationError("Invalid password")

        # 3. Check business rules (domain)
        if not user.is_active:
            raise AuthenticationError("Account inactive")

        # 4. Issue token pair (infrastructure, via application port)
        access_token, refresh_token = (
            self._token_pair_issuer.issue_token_pair(user.id_)
        )

        return LogInResult(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._token_pair_issuer.access_token_expiry_seconds,
        )
```

**Step 3: Domain Service (Domain)**

```python
# domain/user/services.py
class UserService:
    def __init__(
        self,
        user_id_generator: UserIdGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher

    async def is_password_valid(
        self,
        user: User,
        raw_password: RawPassword,
    ) -> bool:
        """Verify password against stored hash."""
        return await self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=user.password_hash,
        )
```

**Step 4: Token Issuance (Infrastructure)**

```python
# infrastructure/security/refresh_token_service.py
class RefreshTokenService(TokenPairIssuer, TokenPairRefresher):
    """
    Infrastructure service responsibilities:
    - Encode JWT access tokens (short-lived, stateless)
    - Generate and persist refresh tokens (long-lived, server-side)
    - Rotate refresh tokens on use
    - Revoke all tokens for a user (on deactivation/deletion)
    """

    def issue_token_pair(self, user_id: UserId) -> tuple[str, str]:
        # 1. Create refresh token and persist to database
        refresh_token = self._create_refresh_token(user_id)
        self._repository.add(refresh_token)

        # 2. Create JWT access token
        access_token = self._create_access_token(user_id)

        return access_token, refresh_token.id_
```

### Data Flow

```
HTTP Request                  Domain / Application             Infrastructure
    │                             │                               │
    │  LogInCommand              │                               │
    │  (dataclass)               │                               │
    ├──────────────▶             │                               │
    │                             │  User                        │
    │                             │  (aggregate root)            │
    │                             ├──────── load ───────────────▶│ DB SELECT
    │                             │                               │
    │                             │  PasswordHasher.verify()     │
    │                             ├──────── verify ─────────────▶│ bcrypt
    │                             │                               │
    │                             │  TokenPairIssuer             │
    │                             │  .issue_token_pair()         │
    │                             ├──────── issue ──────────────▶│ JWT + DB INSERT
    │                             │                               │
    │  TokenResponse              │                               │
    │  (access_token,            │                               │
    │   refresh_token,           │                               │
    │   expires_in)              │                               │
    ◄──────────────              │                               │
```

### Key Observations

**Separation of Concerns:**
- HTTP layer only knows about HTTP (request/response models, status codes)
- Application layer only orchestrates (no HTTP, no SQL, no JWT)
- Domain layer only knows business logic (password verification, user status)
- Infrastructure layer handles technical details (JWT encoding, token storage, database)

**Authentication as Infrastructure:**
- Token management (JWT + refresh tokens) lives entirely in infrastructure
- The application layer uses the `TokenPairIssuer` port — it doesn't know about JWTs
- Refresh tokens are stored server-side for revocability; access tokens are stateless

**Dependency Direction:**
- HTTP Controller depends on `LogInUseCase` port (abstraction)
- Application Handler depends on `UserRepository`, `TokenPairIssuer` ports (abstractions)
- Infrastructure implements those ports (`SqlaUserRepository`, `RefreshTokenService`)
- Domain has zero dependencies on outer layers

**Testing Strategy:**
- Test domain in isolation with no infrastructure
- Test application with in-memory repositories and mock token issuers
- Test HTTP with mocked use cases
- Integration tests exercise the full stack

## Dependency Inversion

The **dependency inversion** technique enables reversing dependencies **by
introducing an interface** between components, allowing an inner layer to
communicate with an outer layer while adhering to the Dependency Rule.

<p align="center">
  <img src="docs/dep_graph_inv_corrupted.svg" alt="Corrupted Dependency" />
  <br><em>Figure 4: <b>Corrupted</b> Dependency</em>
</p>

In this example, the Application component depends directly on the
Infrastructure component, violating the Dependency Rule. This creates
"corrupted" dependencies, where changes in the Infrastructure layer can
propagate to and unintentionally affect the Application layer.

<p align="center">
  <img src="docs/dep_graph_inv_correct.svg" alt="Correct Dependency" />
  <br><em>Figure 5: <b>Correct</b> Dependency</em>
</p>

In the correct design, the Application layer component depends on an
**abstraction (port)**, and the Infrastructure layer component **implements**
the corresponding interface. This makes the Infrastructure component an adapter
for the port, effectively turning it into a plugin for Application layer. Such a
design adheres to the **Dependency Inversion Principle (DIP)**, minimizing the
impact of infrastructure changes on core business logic.

## Dependency Injection

The idea behind **Dependency Injection** is that a component shouldn't create
the dependencies it needs but rather receive them. From this definition, it's
clear that one common way to implement DI is by passing dependencies as
arguments to the `__init__` method or functions.

But how exactly should these dependencies be initialized (and finalized)?

**DI frameworks** offer an elegant solution by automatically creating necessary
objects (while managing their **lifecycle**) and injecting them where needed.
This makes the process of dependency injection much cleaner and easier to
manage.

<p align="center">
  <img src="docs/dep_graph_inv_correct_di.svg" alt="Correct Dependency with DI" />
  <br><em>Figure 6: <b>Correct</b> Dependency <b>with DI</b></em>
</p>

FastAPI provides a built-in **DI mechanism** called
[Depends](https://fastapi.tiangolo.com/tutorial/dependencies/), which tends to
leak into different layers of the application. This creates tight coupling to
FastAPI, violating the principles of Clean Architecture, where the web framework
belongs to the outermost layer and should remain easily replaceable.

Refactoring the codebase to remove `Depends` when switching frameworks can be
unnecessarily costly. It also has
[other limitations](https://dishka.readthedocs.io/en/stable/alternatives.html#why-not-fastapi)
that are beyond the scope of this README. Personally, I prefer
[**Dishka**](https://dishka.readthedocs.io/en/stable/index.html) — a solution
that avoids these issues and remains framework-agnostic.

## CQRS

The project implements Command Query Responsibility Segregation (**CQRS**) — a
pattern that separates read and write operations into distinct paths.

- **Commands** (via interactors) handle write operations and business-critical
  reads using command gateways that work with entities and value objects.
- **Queries** are implemented through query services (similar contract to
  interactors) that use query gateways to fetch data optimized for presentation
  as query models.

This separation enables:

- Efficient read operations through specialized query gates, avoiding loading
  complete entity models.
- Performance optimization by tailoring data retrieval to specific view
  requirements.
- Flexibility to combine data from multiple models in read operations with
  minimal field selection.

# Project

## Dependency Graphs

> [!NOTE]
> The following diagrams illustrate general dependency patterns and architectural principles. While the specific terminology and structure have evolved, the core dependency principles (dependency inversion, ports and adapters, layered architecture) remain fundamental to this implementation.

<details>
  <summary>HTTP Controller - Use Case Handler</summary>

<p align="center">
  <img src="docs/application_controller_interactor.svg" alt="Application Controller - Interactor" />
  <br><em>Figure 7: HTTP Controller invoking Use Case Handler</em>
  </p>

In the infrastructure layer (HTTP controllers), Pydantic models are used when working with FastAPI
to display detailed information in OpenAPI documentation. You
might also find it convenient to validate certain fields using Pydantic;
however, be cautious to avoid leaking business rules into the controller
layer.

For command data in the application layer, a plain `dataclass` is often sufficient. Unlike lighter
alternatives, it provides attribute access, which is more convenient for working
in the application layer. However, such access is unnecessary for data returned
to the client, where a `TypedDict` is sufficient (it's approximately twice as
fast to create as a dataclass with slots, with comparable access times).

</details>

<details>
  <summary>Application Use Case Handler</summary>

<p align="center">
  <img src="docs/application_interactor.svg" alt="Application Interactor" />
  <br><em>Figure 8: Application Use Case Handler dependencies</em>
  </p>

</details>

<details>
  <summary>Application Handler - Repository Adapter</summary>

<p align="center">
  <img src="docs/application_interactor_adapter.svg" alt="Application Interactor - Adapter" />
  <br><em>Figure 9: Application Handler interacting with Repository (via domain port)</em>
  </p>

</details>

<details>
  <summary>Domain - Adapter</summary>

<p align="center">
  <img src="docs/domain_adapter.svg" alt="Domain - Adapter" />
  <br><em>Figure 10: Domain - Adapter</em>
  </p>

</details>

<details>
  <summary>HTTP Controller - Application Handler</summary>
  <p align="center">
  <img src="docs/infrastructure_controller_handler.svg" alt="Infrastructure Controller - Handler" />
  <br><em>Figure 11: HTTP Controller invoking Application Handler through port abstraction</em>
  </p>

This diagram shows how HTTP controllers (infrastructure layer) depend on application use case ports (abstractions)
rather than concrete implementations. The controller invokes the use case through an interface,
allowing the application layer to remain independent of HTTP concerns.

In this architecture:
- HTTP controllers live in `infrastructure/http/controllers/`
- They depend on use case ports (interfaces) like `LogInUseCase`, `CreateUserUseCase`
- Concrete handlers live in `application/` and implement these ports
- Dependency injection wires up the concrete implementations

</details>

<details>
  <summary>Repository Implementation Pattern</summary>
  <p align="center">
  <img src="docs/infrastructure_handler.svg" alt="Infrastructure Handler" />
  <br><em>Figure 12: Repository implementing domain port</em>
  </p>

This diagram illustrates how infrastructure repositories implement domain-defined ports (interfaces).
The repository depends on both the domain port it implements and the infrastructure
technologies (SQLAlchemy, ORM models) it uses.

In this architecture:
- Domain defines repository interfaces (ports) like `UserRepository`
- Infrastructure implements these ports: `SqlaUserRepository`
- The repository translates between domain entities and ORM models
- Application layer depends on the port, not the concrete implementation

</details>

<details>
<summary>Identity Provider Pattern</summary>
  <p align="center">
  <img src="docs/identity_provider.svg" alt="Identity Provider" />
  <br><em>Figure 13: Identity Provider abstracting authentication details</em>
  </p>

**Identity Provider (IdP)** abstracts authentication details, serving as a bridge between
the HTTP layer and the application layer. In this architecture:

- The IdP extracts user identity from JWT Bearer tokens in the `Authorization` header
- It provides the current user's ID without exposing authentication mechanisms
- Domain remains unaware of how authentication works (tokens, etc.)
- Application layer uses IdP to get current user context

The `JwtBearerIdentityProvider` (infrastructure) decodes the JWT access token and
extracts the user ID, abstracting all token details from the application layer.

</details>

## Structure

This project implements **Domain-Driven Design** with **Clean Architecture** using a layer-based organization. Code is organized into three distinct layers (domain, application, infrastructure) with aggregates representing bounded contexts.

```
.
├── config/...                                   # configuration files and Docker setup
├── Makefile                                     # development task automation
├── scripts/...                                  # utility scripts (dependency plotting, etc.)
├── pyproject.toml                               # project metadata and tooling config
└── src/
    ├── run.py                                   # application entry point
    │
    ├── domain/                                  # DOMAIN LAYER - Core business logic
    │   │                                        # (NO external dependencies)
    │   ├── user/                                # User aggregate (bounded context)
    │   │   ├── entity.py                        # User aggregate root
    │   │   ├── value_objects.py                 # UserId, Username, UserPasswordHash, RawPassword
    │   │   ├── events.py                        # UserCreated, UserActivated, UserRoleChanged, etc.
    │   │   ├── enums.py                         # UserRole enum
    │   │   ├── services.py                      # Domain services + permission framework
    │   │   ├── repository.py                    # UserRepository interface (DRIVEN PORT)
    │   │   ├── ports.py                         # PasswordHasher, IdentityProvider, AccessRevoker
    │   │   └── errors.py                        # Domain exceptions
    │   │
    │   └── shared/                              # Shared domain building blocks
    │       ├── aggregate_root.py                # Base aggregate root class
    │       ├── domain_event.py                  # Base domain event class
    │       ├── entity.py                        # Base entity classes
    │       ├── value_object.py                  # Base value object classes
    │       ├── queries.py                       # Shared query types
    │       └── errors.py                        # Common domain exceptions
    │
    ├── application/                             # APPLICATION LAYER - Use cases
    │   │                                        # (Orchestrates domain + infrastructure)
    │   ├── log_in/                              # Log in use case → returns token pair
    │   │   ├── handler.py                       # LogInHandler
    │   │   ├── command.py                       # LogInCommand, LogInResult
    │   │   └── port.py                          # LogInUseCase interface (DRIVER PORT)
    │   │
    │   ├── refresh_token/                       # Refresh token use case → rotates token pair
    │   │   ├── handler.py                       # RefreshTokenHandler
    │   │   ├── command.py                       # RefreshTokenCommand, RefreshTokenResult
    │   │   └── port.py                          # RefreshTokenUseCase interface
    │   │
    │   ├── sign_up/                             # Sign up use case
    │   │   ├── handler.py                       # SignUpHandler
    │   │   ├── command.py                       # SignUpCommand DTO
    │   │   └── port.py                          # SignUpUseCase interface (DRIVER PORT)
    │   │
    │   ├── create_user/                         # Create user use case
    │   │   ├── handler.py
    │   │   ├── command.py
    │   │   └── port.py
    │   │
    │   ├── activate_user/                       # Activate user use case
    │   ├── deactivate_user/                     # Deactivate user use case
    │   ├── grant_admin/                         # Grant admin use case
    │   ├── revoke_admin/                        # Revoke admin use case
    │   ├── set_user_password/                   # Set password use case
    │   ├── change_password/                     # Change password use case
    │   ├── list_users/                          # List users use case
    │   ├── current_user/                        # Current user query
    │   │
    │   └── shared/                              # Shared application layer
    │       ├── unit_of_work.py                  # Transaction abstraction
    │       ├── event_dispatcher.py              # EventDispatcher protocol
    │       ├── token_pair_issuer.py             # TokenPairIssuer protocol
    │       └── token_pair_refresher.py          # TokenPairRefresher protocol
    │
    └── infrastructure/                          # INFRASTRUCTURE LAYER - Adapters
        │                                        # (External systems and frameworks)
        ├── http/                                # REST adapters (DRIVER ADAPTERS)
        │   ├── controllers/                     # HTTP request handlers
        │   │   ├── account/                     # Account-related endpoints
        │   │   │   ├── log_in.py                # POST /login → TokenResponse
        │   │   │   ├── sign_up.py               # POST /signup
        │   │   │   ├── refresh.py               # POST /refresh → TokenResponse
        │   │   │   └── change_password.py       # PUT /password
        │   │   └── user/                        # User-related endpoints
        │   │       ├── create_user.py
        │   │       ├── activate_user.py
        │   │       ├── deactivate_user.py
        │   │       ├── grant_admin.py
        │   │       ├── revoke_admin.py
        │   │       ├── set_user_password.py
        │   │       └── list_users.py
        │   ├── routers/                         # FastAPI routers
        │   │   ├── account_router.py
        │   │   ├── user_router.py
        │   │   ├── api_v1_router.py
        │   │   └── root_router.py
        │   ├── schemas/                         # Response/request schemas
        │   │   ├── token_response.py            # TokenResponse (access + refresh + expires_in)
        │   │   └── refresh_request.py           # RefreshRequest
        │   ├── middleware/                       # HTTP middleware
        │   └── errors/                          # Error translators, handlers
        │
        ├── persistence/                         # Database adapters (DRIVEN ADAPTERS)
        │   ├── sqla_user_repository.py          # SqlaUserRepository (implements UserRepository)
        │   ├── sqla_refresh_token_repository.py # SqlaRefreshTokenRepository
        │   ├── sqla_unit_of_work.py             # SqlaUnitOfWork
        │   ├── mappers/                         # Entity-to-model mappers
        │   │   ├── user.py                      # User entity <-> users table
        │   │   └── refresh_token.py             # RefreshToken <-> refresh_tokens table
        │   └── ...                              # registry, constants, types
        │
        ├── security/                            # Security implementations
        │   ├── password_hasher_bcrypt.py         # BcryptPasswordHasher (HMAC pepper + bcrypt)
        │   ├── access_token_processor_jwt.py     # JwtAccessTokenProcessor (JWT encode/decode)
        │   ├── refresh_token_service.py          # RefreshTokenService (TokenPairIssuer + Refresher)
        │   ├── refresh_token.py                  # RefreshToken dataclass
        │   ├── refresh_token_repository.py       # RefreshTokenRepository protocol
        │   ├── refresh_token_id_generator.py     # StrRefreshTokenIdGenerator (secrets.token_urlsafe)
        │   ├── identity_provider.py              # JwtBearerIdentityProvider (Bearer auth)
        │   ├── access_revoker.py                 # RefreshTokenAccessRevoker
        │   └── user_id_generator_uuid.py         # UuidUserIdGenerator
        │
        ├── events/                              # Event handling infrastructure
        │   └── in_process_dispatcher.py         # InProcessEventDispatcher
        │
        └── config/                              # Application configuration
            ├── app_factory.py                   # FastAPI app factory
            ├── di/                              # Dependency injection (Dishka)
            │   ├── provider_registry.py         # Provider registry
            │   ├── domain.py                    # Domain service providers
            │   ├── application.py               # Application service providers
            │   ├── infrastructure.py            # Infrastructure providers
            │   └── settings.py                  # Settings providers
            └── settings/                        # Settings management
                ├── app_settings.py              # AppSettings
                ├── loader.py                    # Config file loader
                ├── database.py                  # Database settings
                ├── security.py                  # AuthSettings + PasswordSettings
                └── logs.py                      # Logging configuration
```

### Key Architecture Patterns

**Layer-Based DDD:**
- Business logic organized into **aggregates** (User) representing bounded contexts
- Each aggregate defines a **consistency boundary** for transactions
- Authentication (JWT + refresh tokens) is an infrastructure concern, not a domain aggregate
- Clear separation: Domain → Application → Infrastructure
- Dependencies flow inward: Infrastructure depends on Application depends on Domain

**Aggregate Structure:**
- **Aggregate Root**: Entry point for all operations (User entity)
- **Domain Events**: Record state changes (UserCreated, UserActivated)
- **Value Objects**: Immutable business types (UserId, Username)
- **Repository Interfaces**: Persistence abstractions defined in domain
- **Domain Services**: Stateless business logic

**Application Layer (Use Cases):**
- **Command**: Input DTO for use case (LogInCommand)
- **Handler**: Orchestrates domain logic + infrastructure (LogInHandler)
- **Port**: Interface defining use case contract (LogInUseCase)
- Handlers coordinate multiple domain services and repositories
- All business logic delegated to domain layer

**Dependency Rule:**
- Dependencies point inward: Infrastructure → Application → Domain
- Domain has **zero dependencies** on frameworks or infrastructure
- Application depends on domain abstractions (ports)
- Infrastructure implements domain ports (adapters)

**CQRS Pattern:**
- Write operations: Commands flow through handlers → domain services → repository
- Read operations: Queries can bypass domain for optimized reads
- Separate models for commands and queries where beneficial

## Makefile Commands Reference

The project includes a comprehensive Makefile for automating common development tasks. Run `make help` to see all available commands.

### Environment Management

- `make env.local` - Print command to set APP_ENV=local (run in shell: `eval $(make env.local)`)
- `make env` - Display current APP_ENV value
- `make dotenv` - Generate .env files from config templates
- `make venv` - Create or update virtual environment using uv
- `make venv.activate` - Print command to activate virtual environment
- `make venv.deactivate` - Print command to deactivate virtual environment

### Database Management (Supabase)

- `make up.db` - Start Supabase local database
- `make up.db-echo` - Start Supabase local database with debug output
- `make down.db` - Stop Supabase local database
- `make logs.db` - Tail Supabase database container logs
- `make shell.db` - Open interactive shell inside Supabase database container

### Docker Compose (Application)

- `make up` - Start application containers in detached mode
- `make up.echo` - Start application containers in foreground (with logs)
- `make down` - Stop application containers
- `make down.total` - Stop application containers and remove volumes
- `make prune` - Clean up docker compose artifacts (stopped containers, networks, etc.)

### Code Quality

- `make code.format` - Format code using ruff
- `make code.lint` - Run linters (ruff, slotscheck, mypy)
- `make code.test` - Run pytest test suite
- `make code.cov` - Run tests with coverage and print report
- `make code.cov.html` - Run tests with coverage and generate HTML report
- `make code.check` - Run full quality check (lint + test)

### Project Utilities

- `make pycache-del` - Remove all __pycache__ directories
- `make tree` - Display project tree structure (after cleaning)
- `make plot-data` - Plot Dishka dependency injection graph
- `make help` - Display this help information

## Technology Stack

- **Python**: `3.13`
- **Core**: `bcrypt`, `dishka`, `fastapi-error-map`, `fastapi`, `orjson`,
  `psycopg[binary]`, `pyjwt[crypto]`, `sqlalchemy[mypy]`, `uuid-utils`,
  `uvicorn`, `uvloop`
- **Development**: `mypy`, `pre-commit`, `ruff`, `slotscheck`
- **Testing**: `coverage`, `line-profiler`, `pytest`, `pytest-asyncio`

## API

<p align="center">
  <img src="docs/handlers.png" alt="Handlers" />
  <br><em>Figure 14: Handlers</em>
</p>

### General

- `/` (GET): Open to **everyone**.
  - Redirects to Swagger documentation.
- `/api/v1/health` (GET): Open to **everyone**.
  - Returns `200 OK` if the API is alive.

### Account (`/api/v1/account`)

- `/signup` (POST): Open to **everyone**.
  - Registers a new user with validation and uniqueness checks.
  - Passwords are peppered (HMAC-SHA384), salted, and stored as bcrypt hashes.
  - Returns a JWT access token and refresh token upon successful registration.
- `/login` (POST): Open to **everyone**.
  - Authenticates a registered user by verifying credentials.
  - Returns a JWT access token (short-lived) and a refresh token (long-lived,
    stored server-side).
  - Access tokens are stateless and verified cryptographically.
  - Protected endpoints require `Authorization: Bearer <access_token>` header.
- `/refresh` (POST): Open to **everyone** (with valid refresh token).
  - Accepts a refresh token and rotates it: the old token is deleted and a new
    token pair (access + refresh) is issued.
  - Returns `401` if the refresh token is not found or expired.
- `/password` (PUT): Open to **authenticated users**.
  - The current user can change their password.
  - New password must differ from current password.

### Users (`/api/v1/users`)

- `/` (POST): Open to **admins**.
  - Creates a new user, including admins, if the username is unique.
  - Only super admins can create new admins.
- `/` (GET): Open to **admins**.
  - Retrieves a paginated list of existing users with relevant information.
- `/{user_id}/password` (PUT): Open to **admins**.
  - Admins can set passwords of subordinate users.
- `/{user_id}/roles/admin` (PUT): Open to **super admins**.
  - Grants admin rights to a specified user.
  - Super admin rights cannot be changed.
- `/{user_id}/roles/admin` (DELETE): Open to **super admins**.
  - Revokes admin rights from a specified user.
  - Super admin rights cannot be changed.
- `/{user_id}/activation` (PUT): Open to **admins**.
  - Restores a previously soft-deleted user.
  - Only super admins can activate other admins.
- `/{user_id}/activation` (DELETE): Open to **admins**.
  - Soft-deletes an existing user, making that user inactive.
  - Also revokes all of the user's refresh tokens.
  - Only super admins can deactivate other admins.
  - Super admins cannot be soft-deleted.

> [!NOTE]
>
> - Super admin privileges must be initially granted manually (e.g., directly in
>   the database), though the user account itself can be created through the
>   API.

## Configuration

> [!WARNING]
>
> - This part of documentation is **not** related to the architecture approach.
> - Use any configuration method you prefer.

### Files

- **config.toml**: Main application settings organized in sections
- **export.toml**: Lists fields to export to .env
  (`export.fields = ["postgres.USER", "postgres.PASSWORD", ...]`)
- **.secrets.toml**: Optional sensitive data (same format as config.toml, merged
  with main config)

> [!IMPORTANT]
>
> - This project includes secret files for demonstration purposes only. In a
>   real project, you **must** ensure that `.secrets.toml` and all `.env` files
>   are not tracked by version control system to prevent exposing sensitive
>   information. See this project's `.gitignore` for an example of how to
>   properly exclude these sensitive files from Git.

**Security settings** (`config.toml` → `[security.auth]` and `[security.password]`):

| Setting | Section | Description |
|---------|---------|-------------|
| `JWT_ALGORITHM` | `security.auth` | JWT signing algorithm (`HS256`, `HS384`, `HS512`, `RS256`, `RS384`, `RS512`) |
| `ACCESS_TOKEN_EXPIRY_MIN` | `security.auth` | Access token lifetime in minutes (default: 15) |
| `REFRESH_TOKEN_EXPIRY_DAYS` | `security.auth` | Refresh token lifetime in days (default: 7) |
| `HASHER_WORK_FACTOR` | `security.password` | Bcrypt work factor (minimum: 10) |
| `HASHER_MAX_THREADS` | `security.password` | Max threads for password hashing |
| `HASHER_SEMAPHORE_WAIT_TIMEOUT_S` | `security.password` | Fail-fast timeout for password hashing |

**Secrets** (`.secrets.toml`):

| Secret | Section | Description |
|--------|---------|-------------|
| `JWT_SECRET` | `security.auth` | JWT signing key (min 32 characters) |
| `PEPPER` | `security.password` | HMAC pepper for password hashing (min 32 characters) |

### Flow

In this project I use my own configuration system based on TOML files as the
single source of truth. The system generates `.env` files for Docker and
infrastructure components while the application reads settings directly from the
structured TOML files. More details are available at
https://github.com/ivan-borovets/toml-config-manager

<p align="center">
  <img src="docs/toml_config_manager.svg" alt="Configuration flow" />
  <br><em>Figure 15: Configuration flow </em>
  <br><small>Here, the arrows represent usage flow, <b>not dependencies.</b></small>
</p>

### Local Environment

1. Configure local environment

- In this project, local configuration is already prepared in `config/local/`.\
  Nothing needs to be created — adjust files only if you want to change
  defaults.
- If you want to adjust settings, edit the existing TOML files in
  `config/local/` directly.\
  `.env.local` will be generated automatically — **don’t** create or edit it
  manually.
- Docker Compose in this project is already configured with `APP_ENV`.\
  Just keep in mind this variable if you change the setup:

```yaml
services:
  app:
    # ...
    environment:
      APP_ENV: ${APP_ENV}
```

2. Set environment variable

```shell
export APP_ENV=local
# export APP_ENV=dev
# export APP_ENV=prod
```

3. Check it and generate `.env`

```shell
# Probably you'll need Python 3.13 installed on your system to run these commands. 
# The next code section provides commands for its fast installation.
make env  # should print APP_ENV=local
make dotenv  # should tell you where .env.local was generated
```

4. Install `uv`

```shell
# sudo apt update
# sudo apt install pipx
# pipx ensurepath
# pipx install uv
# https://docs.astral.sh/uv/getting-started/installation/#shell-autocompletion
# uv python install 3.13  # To install Python
```

5. Set up virtual environment

```shell
uv sync --group dev
source .venv/bin/activate

# Alternatively,
# uv v
# source .venv/bin/activate  # on Unix
# .venv\Scripts\activate  # on Windows
# uv pip install -e . --group dev
```

Don't forget to tell your IDE where the interpreter is located.

Install pre-commit hooks:

```shell
# https://pre-commit.com/
pre-commit install
```

6. Launch

- To run only the database in Docker and use the app locally, use the following
  command:

  ```shell
  make up.db
  # make up.db-echo
  ```

- Then, start Supabase and apply migrations:
  ```shell
  supabase start
  # Migrations are automatically applied when Supabase starts
  ```

- After Supabase is running, the database is ready, and you can launch the
  application locally (e.g., through your IDE). Remember to set the `APP_ENV`
  environment variable in your IDE's run configuration.

- To run via Docker Compose:

  ```shell
  make up
  # make up.echo
  ```

  In this case, migrations will be applied automatically at startup.

7. Shutdown

- To stop the containers, use:
  ```shell
  make down
  ```

### Other Environments (dev/prod)

1. Use the instructions about [local environment](#local-environment) above

- But make sure you've created similar structure in `config/dev` or
  `config/prod` with [files](#files):
  - `config.toml`
  - `.secrets.toml`
  - `export.toml`
  - `docker-compose.yaml` if needed
- `.env.dev` or `.env.prod` to be generated later — **don't** create them
  manually

### Adding New Environments

1. Add new value to `ValidEnvs` enum in `config/toml_config_manager.py` (and
   maybe in your app settings)
2. Update `ENV_TO_DIR_PATHS` mapping in the same file (and maybe in your app
   settings)
3. Create corresponding directory in `config/` folder
4. Add required configuration [files](#files)

Environment directories can also contain other env-specific files like
`docker-compose.yaml`, which will be used by Makefile commands.

# Useful Resources

## Layered Architecture

- [Robert C. Martin. Clean Architecture: A Craftsman's Guide to Software Structure and Design. 2017](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)

- [Alistair Cockburn. Hexagonal Architecture Explained. 2024](https://www.amazon.com/Hexagonal-Architecture-Explained-Alistair-Cockburn-ebook/dp/B0D4JQJ8KD)
  (introduced in 2005)

## Domain-Driven Design

- [Vlad Khononov. Learning Domain-Driven Design: Aligning Software Architecture and Business Strategy. 2021](https://www.amazon.com/Learning-Domain-Driven-Design-Aligning-Architecture/dp/1098100131)

- [Vaughn Vernon. Implementing Domain-Driven Design. 2013](https://www.amazon.com/Implementing-Domain-Driven-Design-Vaughn-Vernon/dp/0321834577)

- [Eric Evans. Domain-Driven Design: Tackling Complexity in the Heart of Software. 2003](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)

- [Martin Fowler. Patterns of Enterprise Application Architecture. 2002](https://www.amazon.com/Patterns-Enterprise-Application-Architecture-Martin/dp/0321127420)

## Adjacent

- [Vladimir Khorikov. Unit Testing Principles. 2020](https://www.amazon.com/Unit-Testing-Principles-Practices-Patterns/dp/1617296279)

# ⭐ Support the Project

If you find this project useful, please give it a star or share it! Your support
means a lot.

👉 Check out the amazing
[fastapi-error-map](https://github.com/ivan-borovets/fastapi-error-map), used
here to enable contextual, per-route error handling with automatic OpenAPI
schema generation.

💬 Feel free to open issues, ask questions, or submit pull requests.

# Acknowledgements

I would like to express my sincere gratitude to the following individuals for
their valuable ideas and support in satisfying my curiosity throughout the
development of this project: [igoryuha](https://github.com/igoryuha),
[tishka17](https://github.com/tishka17),
[chessenjoyer17](https://github.com/chessenjoyer17),
[PlzTrustMe](https://github.com/PlzTrustMe),
[Krak3nDev](https://github.com/Krak3nDev),
[Ivankirpichnikov](https://github.com/Ivankirpichnikov),
[SamWarden](https://github.com/SamWarden),
[nkhitrov](https://github.com/nkhitrov),
[ApostolFet](https://github.com/ApostolFet), Lancetnik, Sehat1137, Maclovi.

I also greatly appreciate the valuable insights shared by participants of the
ASGI Community Telegram chat, despite frequent and lively communication
challenges, as well as the ⚗️ Reagento (adaptix/dishka)
[Telegram chat](https://t.me/reagento_ru) for their thoughtful discussions and
generous knowledge exchange.

# Todo

- [x] set up CI
- [x] simplify settings
- [x] simplify annotations
- [ ] add integration tests
- [ ] explain design choices

[^1]: This JWT authentication scheme is **not** related to OAuth 2.0. Access
    tokens are short-lived and stateless (no database lookup on each request).
    Refresh tokens are stored server-side to enable revocation.
