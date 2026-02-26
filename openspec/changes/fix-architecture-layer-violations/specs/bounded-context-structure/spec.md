## MODIFIED Requirements

### Requirement: Shared kernel directory
The `src/shared/` directory SHALL contain domain base classes (`Entity`, `AggregateRoot`, `ValueObject`, `DomainEvent`), shared value objects (`AccountId`), shared ports (`IdentityProvider`, `AuthorizationGuard`), shared errors, pagination/sorting primitives, the event type registry (`event_registry.py`), and cross-cutting infrastructure (event dispatcher, handler registry).

#### Scenario: Shared domain classes available to both contexts
- **WHEN** the Account BC or Core BC imports `AggregateRoot` or `ValueObject`
- **THEN** they import from `shared.domain`

#### Scenario: AccountId in shared kernel
- **WHEN** the Core BC needs to reference an account
- **THEN** it imports `AccountId` from `shared.domain.account_id`

#### Scenario: AuthorizationGuard in shared kernel
- **WHEN** any bounded context needs to check admin authorization
- **THEN** it imports `AuthorizationGuard` from `shared.domain.ports.authorization_guard`

#### Scenario: register_event in shared domain
- **WHEN** a domain event class needs the `register_event` decorator
- **THEN** it imports from `shared.domain.event_registry`

### Requirement: No cross-context domain imports
Bounded contexts SHALL NOT import from each other's domain layers directly. Cross-context communication SHALL use domain events and the shared kernel only. Application-layer handlers in one context SHALL NOT import domain entities, value objects, enums, or repository ports from another context.

#### Scenario: Core references Account identity
- **WHEN** Core BC needs to reference an account
- **THEN** it uses `AccountId` from the shared kernel, NOT from `account.domain`

#### Scenario: Cross-context event handler
- **WHEN** Core BC handles `AccountCreated` event
- **THEN** the event type is defined in Account BC's domain, but the handler lives in Core BC's infrastructure, and the event is received via the shared event dispatcher

#### Scenario: Core application has no Account domain imports
- **WHEN** inspecting any file under `core/application/`
- **THEN** there are no imports from `account.domain`
