## ADDED Requirements

### Requirement: Account aggregate root
The `Account` class SHALL extend `AggregateRoot[AccountId]` and be located at `account/domain/account/entity.py`. It SHALL hold: `id_: AccountId`, `email: Email`, `password_hash: AccountPasswordHash`, `role: AccountRole`, `is_active: bool`.

#### Scenario: Create account with default role
- **WHEN** `Account.create(id_, email, password_hash)` is called without explicit role
- **THEN** account is created with `role=AccountRole.USER`, `is_active=True`, and an `AccountCreated` event is registered

#### Scenario: Create account with explicit assignable role
- **WHEN** `Account.create(id_, email, password_hash, role=AccountRole.ADMIN)` is called
- **THEN** account is created with role ADMIN and an `AccountCreated` event is registered

#### Scenario: Create account with non-assignable role
- **WHEN** `Account.create(id_, email, password_hash, role=AccountRole.SUPER_ADMIN)` is called
- **THEN** `RoleAssignmentNotPermittedError` is raised

### Requirement: Email value object
The `Email` value object SHALL be located at `account/domain/account/value_objects.py`. It SHALL validate email format and store the value as a string. Maximum length SHALL be 255 characters.

#### Scenario: Valid email
- **WHEN** `Email("user@example.com")` is constructed
- **THEN** the value object is created successfully

#### Scenario: Invalid email format
- **WHEN** `Email("not-an-email")` is constructed
- **THEN** a `DomainTypeError` is raised

### Requirement: AccountPasswordHash value object
The `AccountPasswordHash` value object SHALL be located at `account/domain/account/value_objects.py`. It SHALL wrap `bytes` and behave identically to the former `UserPasswordHash`.

#### Scenario: Construct password hash
- **WHEN** `AccountPasswordHash(b"hashed_bytes")` is constructed
- **THEN** the value object is created with the bytes value

### Requirement: RawPassword value object
The `RawPassword` value object SHALL remain functionally identical to the current implementation but be located at `account/domain/account/value_objects.py`. Minimum length SHALL be 6 characters.

#### Scenario: Valid raw password
- **WHEN** `RawPassword("secure123")` is constructed
- **THEN** the value object is created and the value is encoded to bytes

#### Scenario: Too short password
- **WHEN** `RawPassword("short")` is constructed
- **THEN** a `DomainTypeError` is raised

### Requirement: AccountRole enum
The `AccountRole` enum SHALL be located at `account/domain/account/enums.py`. It SHALL contain `SUPER_ADMIN`, `ADMIN`, `USER` values with `is_assignable` and `is_changeable` properties. The `SUBORDINATE_ROLES` mapping SHALL be defined in the same module.

#### Scenario: SUPER_ADMIN is not assignable
- **WHEN** `AccountRole.SUPER_ADMIN.is_assignable` is checked
- **THEN** it returns False

#### Scenario: ADMIN subordinate roles
- **WHEN** `SUBORDINATE_ROLES[AccountRole.ADMIN]` is accessed
- **THEN** it returns `{AccountRole.USER}`

### Requirement: Account activation behavior
The Account aggregate SHALL support `activate()` and `deactivate()` methods. SUPER_ADMIN accounts SHALL NOT be activatable or deactivatable. Methods SHALL return `bool` indicating state change and register corresponding events.

#### Scenario: Activate inactive account
- **WHEN** `activate()` is called on an inactive non-SUPER_ADMIN account
- **THEN** `is_active` becomes True, `AccountActivated` event is registered, returns True

#### Scenario: Activate already active account
- **WHEN** `activate()` is called on an already active account
- **THEN** no event is registered, returns False

#### Scenario: Activate SUPER_ADMIN account
- **WHEN** `activate()` is called on a SUPER_ADMIN account
- **THEN** `ActivationChangeNotPermittedError` is raised

#### Scenario: Deactivate active account
- **WHEN** `deactivate()` is called on an active non-SUPER_ADMIN account
- **THEN** `is_active` becomes False, `AccountDeactivated` event is registered, returns True

### Requirement: Account role change behavior
The Account aggregate SHALL support `change_role(new_role)`. SUPER_ADMIN accounts SHALL NOT have their role changed. Method SHALL return `bool` indicating change and register `AccountRoleChanged` event.

#### Scenario: Change role of regular account
- **WHEN** `change_role(AccountRole.ADMIN)` is called on a USER account
- **THEN** role changes, `AccountRoleChanged` event is registered with old and new roles, returns True

#### Scenario: Change role of SUPER_ADMIN
- **WHEN** `change_role(AccountRole.USER)` is called on a SUPER_ADMIN account
- **THEN** `RoleChangeNotPermittedError` is raised

### Requirement: Account password change
The Account aggregate SHALL support `change_password(new_hash)` which updates the password hash and registers an `AccountPasswordChanged` event.

#### Scenario: Change password
- **WHEN** `change_password(new_hash)` is called
- **THEN** password hash is updated and `AccountPasswordChanged` event is registered

### Requirement: AccountRepository protocol
The `AccountRepository` protocol SHALL be located at `account/domain/account/repository.py`. It SHALL define: `save(account)`, `get_by_id(account_id, for_update=False)`, `get_by_email(email, for_update=False)`, `get_all(pagination, sorting)`.

#### Scenario: Get account by email
- **WHEN** `get_by_email(Email("user@example.com"))` is called
- **THEN** returns the Account if found, None otherwise

#### Scenario: Get all accounts with pagination
- **WHEN** `get_all(pagination, sorting)` is called
- **THEN** returns `ListAccountsQM` with `accounts` list and `total` count

### Requirement: AccountService domain service
The `AccountService` SHALL be located at `account/domain/account/services.py`. It SHALL provide `create(email, raw_password, role, is_active)`, `is_password_valid(account, raw_password)`, and `change_password(account, raw_password)` methods using `AccountIdGenerator` and `PasswordHasher` ports.

#### Scenario: Create account via service
- **WHEN** `AccountService.create(email, raw_password)` is called
- **THEN** generates an AccountId, hashes the password, and returns an Account with `AccountCreated` event

### Requirement: Account permission framework
The permission framework SHALL be located at `account/domain/account/services.py`. It SHALL contain `CanManageSelf`, `CanManageSubordinate`, `CanManageRole` permissions using `AccountManagementContext` and `RoleManagementContext`. The `Permission`, `AnyOf`, and `authorize` base types SHALL be in the shared kernel.

#### Scenario: Self-management permission
- **WHEN** `CanManageSelf` is evaluated with subject == target
- **THEN** permission is satisfied

#### Scenario: Subordinate management
- **WHEN** an ADMIN evaluates `CanManageSubordinate` against a USER target
- **THEN** permission is satisfied

### Requirement: Account domain errors
Account-specific errors SHALL be located at `account/domain/account/errors.py`: `EmailAlreadyExistsError`, `AccountNotFoundByIdError`, `AccountNotFoundByEmailError`, `ActivationChangeNotPermittedError`, `RoleAssignmentNotPermittedError`, `RoleChangeNotPermittedError`.

#### Scenario: Email already exists error
- **WHEN** `EmailAlreadyExistsError(email)` is raised
- **THEN** the error contains the duplicate email value

### Requirement: Account domain ports
`PasswordHasher`, `AccessRevoker`, and `AccountIdGenerator` ports SHALL be located at `account/domain/account/ports.py`.

#### Scenario: Generate account ID
- **WHEN** `AccountIdGenerator.generate()` is called
- **THEN** a new unique `AccountId` is returned
