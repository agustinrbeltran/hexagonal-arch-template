## MODIFIED Requirements

### Requirement: Account aggregate root
The `Account` class SHALL extend `AggregateRoot[AccountId]` and be located at `account/domain/account/entity.py`. It SHALL hold: `id_: AccountId`, `email: Email`, `role: AccountRole`, `is_active: bool`. The `email` field is read-only (no `change_email()` method). The `password_hash` field is removed.

#### Scenario: Create account with default role
- **WHEN** `Account.create(id_, email)` is called without explicit role
- **THEN** account is created with `role=AccountRole.USER`, `is_active=True`, and an `AccountCreated` event is registered

#### Scenario: Create account with explicit assignable role
- **WHEN** `Account.create(id_, email, role=AccountRole.ADMIN)` is called
- **THEN** account is created with role ADMIN and an `AccountCreated` event is registered

#### Scenario: Create account with non-assignable role
- **WHEN** `Account.create(id_, email, role=AccountRole.SUPER_ADMIN)` is called
- **THEN** `RoleAssignmentNotPermittedError` is raised

### Requirement: AccountRepository protocol
The `AccountRepository` protocol SHALL be located at `account/domain/account/repository.py`. It SHALL define: `save(account)`, `get_by_id(account_id, for_update=False)`, `get_by_email(email, for_update=False)`, `get_all(pagination, sorting)`. The `save()` method persists only account metadata (role, is_active) to `public.account_metadata`. The `get_by_*` methods reconstruct the full `Account` aggregate by joining `auth.users` (for email) with `account_metadata` (for role, is_active).

#### Scenario: Get account by email
- **WHEN** `get_by_email(Email("user@example.com"))` is called
- **THEN** returns the Account if found (with email from `auth.users` and role/is_active from `account_metadata`), None otherwise

#### Scenario: Get all accounts with pagination
- **WHEN** `get_all(pagination, sorting)` is called
- **THEN** returns `ListAccountsQM` with `accounts` list and `total` count

#### Scenario: Save persists metadata only
- **WHEN** `save(account)` is called
- **THEN** only `account_id`, `role`, and `is_active` are persisted to `account_metadata`

### Requirement: Account domain ports
The `account/domain/account/ports.py` file SHALL contain only `AccessRevoker`. The `PasswordHasher` and `AccountIdGenerator` ports are removed.

#### Scenario: AccessRevoker port exists
- **WHEN** inspecting `account/domain/account/ports.py`
- **THEN** it defines the `AccessRevoker` protocol

#### Scenario: PasswordHasher port is removed
- **WHEN** inspecting `account/domain/account/ports.py`
- **THEN** no `PasswordHasher` protocol exists

#### Scenario: AccountIdGenerator port is removed
- **WHEN** inspecting `account/domain/account/ports.py`
- **THEN** no `AccountIdGenerator` protocol exists

## REMOVED Requirements

### Requirement: AccountPasswordHash value object
**Reason**: Credentials are managed by the external auth provider. The domain no longer stores or handles password hashes.
**Migration**: Remove all references to `AccountPasswordHash`. The `Account` entity no longer has a `password_hash` field.

### Requirement: Account password change
**Reason**: Password changes are delegated to the external auth provider via the `PasswordResetter` application-layer port.
**Migration**: Remove `change_password()` from the `Account` entity. Remove `AccountPasswordChanged` event. Use `PasswordResetter.reset_password()` in the `ChangePasswordHandler`.

### Requirement: AccountService domain service
**Reason**: All `AccountService` responsibilities (ID generation, password hashing, password verification, password changing) are delegated to application-layer ports backed by the external auth provider. The permission classes (`CanManageSelf`, `CanManageSubordinate`, `CanManageRole`) remain as standalone classes in `services.py`.
**Migration**: Remove `AccountService` class. Handlers call `AccountProvisioner.register()` for sign-up, `TokenPairIssuer.issue_token_pair()` for login, and `PasswordResetter.reset_password()` for password changes. `Account.create()` is called directly by handlers.
