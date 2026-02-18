## REMOVED Requirements

### Requirement: User aggregate root at domain/user/entity.py
**Reason**: Replaced by `Account` aggregate in Account BC (`account/domain/account/entity.py`) and `Profile` aggregate in Core BC (`core/domain/profile/entity.py`).
**Migration**: All auth/access fields (password_hash, role, is_active) move to Account. Username moves to Profile. Email replaces username as the login identifier on Account.

### Requirement: User value objects at domain/user/value_objects.py
**Reason**: Replaced by Account and Profile value objects in their respective bounded contexts. `UserId` → `AccountId` (shared kernel), `Username` → `core/domain/profile/value_objects.py`, `UserPasswordHash` → `AccountPasswordHash`, `RawPassword` → `account/domain/account/value_objects.py`.
**Migration**: Import paths change to bounded context locations. New `Email` value object added to Account.

### Requirement: User domain events at domain/user/events.py
**Reason**: Replaced by Account domain events (`AccountCreated`, `AccountActivated`, `AccountDeactivated`, `AccountRoleChanged`, `AccountPasswordChanged`) in `account/domain/account/events.py` and Profile events (`ProfileCreated`, `UsernameChanged`) in `core/domain/profile/events.py`.
**Migration**: All event consumers update to new event types and import paths.

### Requirement: User repository port at domain/user/repository.py
**Reason**: Replaced by `AccountRepository` in `account/domain/account/repository.py` and `ProfileRepository` in `core/domain/profile/repository.py`. `get_by_username()` replaced by `get_by_email()` on AccountRepository and `get_by_account_id()` on ProfileRepository.
**Migration**: All repository consumers update to new types and import paths.

### Requirement: User domain services at domain/user/services.py
**Reason**: Replaced by `AccountService` in `account/domain/account/services.py`. Permission framework moves to Account BC with Account-prefixed context types.
**Migration**: `UserService` → `AccountService`. Permission contexts renamed to `AccountManagementContext`, `RoleManagementContext`.

### Requirement: User domain errors at domain/user/errors.py
**Reason**: Replaced by Account errors (`EmailAlreadyExistsError`, `AccountNotFoundByIdError`, `AccountNotFoundByEmailError`, etc.) in `account/domain/account/errors.py` and Profile errors (`UsernameAlreadyExistsError`, `ProfileNotFoundByIdError`, etc.) in `core/domain/profile/errors.py`.
**Migration**: All error consumers update to new types and import paths.
