## ADDED Requirements

### Requirement: Shared kernel directory
The `src/shared/` directory SHALL contain domain base classes (`Entity`, `AggregateRoot`, `ValueObject`, `DomainEvent`), shared value objects (`AccountId`), shared ports (`IdentityProvider`), shared errors, pagination/sorting primitives, and cross-cutting infrastructure (event dispatcher, event registry).

#### Scenario: Shared domain classes available to both contexts
- **WHEN** the Account BC or Core BC imports `AggregateRoot` or `ValueObject`
- **THEN** they import from `shared.domain`

#### Scenario: AccountId in shared kernel
- **WHEN** the Core BC needs to reference an account
- **THEN** it imports `AccountId` from `shared.domain.account_id`

### Requirement: Account bounded context directory
The `src/account/` directory SHALL contain `domain/`, `application/`, and `infrastructure/` subdirectories. All account-related aggregates, use cases, and adapters SHALL reside here.

#### Scenario: Account aggregate location
- **WHEN** looking for the Account aggregate
- **THEN** it is found at `src/account/domain/account/`

#### Scenario: Account use cases location
- **WHEN** looking for account use cases (sign_up, log_in, create_account, etc.)
- **THEN** they are found under `src/account/application/`

### Requirement: Core bounded context directory
The `src/core/` directory SHALL contain `domain/`, `application/`, and `infrastructure/` subdirectories. All core business aggregates (Profile) and their use cases SHALL reside here.

#### Scenario: Profile aggregate location
- **WHEN** looking for the Profile aggregate
- **THEN** it is found at `src/core/domain/profile/`

#### Scenario: Core use cases location
- **WHEN** looking for profile use cases (get_my_profile, set_username, etc.)
- **THEN** they are found under `src/core/application/`

### Requirement: No cross-context domain imports
Bounded contexts SHALL NOT import from each other's domain layers directly. Cross-context communication SHALL use domain events and the shared kernel only.

#### Scenario: Core references Account identity
- **WHEN** Core BC needs to reference an account
- **THEN** it uses `AccountId` from the shared kernel, NOT from `account.domain`

#### Scenario: Cross-context event handler
- **WHEN** Core BC handles `AccountCreated` event
- **THEN** the event type is defined in Account BC's domain, but the handler lives in Core BC's infrastructure, and the event is received via the shared event dispatcher
