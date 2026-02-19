# Design: Fix Unit Test Structure

## New Directory Layout

```
tests/app/unit/
├── account/
│   ├── __init__.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── activate_account/
│   │   │   ├── __init__.py
│   │   │   └── test_activate_account_handler.py
│   │   ├── change_password/
│   │   │   ├── __init__.py
│   │   │   └── test_change_password_handler.py
│   │   ├── create_account/
│   │   │   ├── __init__.py
│   │   │   └── test_create_account_handler.py
│   │   ├── current_account/
│   │   │   ├── __init__.py
│   │   │   └── test_current_account_handler.py
│   │   ├── deactivate_account/
│   │   │   ├── __init__.py
│   │   │   └── test_deactivate_account_handler.py
│   │   ├── grant_admin/
│   │   │   ├── __init__.py
│   │   │   └── test_grant_admin_handler.py
│   │   ├── list_accounts/
│   │   │   ├── __init__.py
│   │   │   └── test_list_accounts_handler.py
│   │   ├── log_in/
│   │   │   ├── __init__.py
│   │   │   └── test_log_in_handler.py          ← moved from old location
│   │   ├── refresh_token/
│   │   │   ├── __init__.py
│   │   │   └── test_refresh_token_handler.py   ← moved from old location
│   │   ├── revoke_admin/
│   │   │   ├── __init__.py
│   │   │   └── test_revoke_admin_handler.py
│   │   ├── set_account_password/
│   │   │   ├── __init__.py
│   │   │   └── test_set_account_password_handler.py
│   │   └── sign_up/
│   │       ├── __init__.py
│   │       └── test_sign_up_handler.py
│   └── domain/
│       ├── __init__.py
│       ├── test_account_entity.py              ← renamed from test_user.py (services tests)
│       ├── test_account_role.py                ← renamed from test_user_role.py
│       ├── test_email.py                       ← renamed from test_username.py
│       ├── test_raw_password.py                ← moved from old location
│       ├── conftest.py                         ← moved from domain/services/
│       └── mock_types.py                       ← moved from domain/services/
├── core/
│   ├── __init__.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── get_my_profile/
│   │   │   ├── __init__.py
│   │   │   └── test_get_my_profile_handler.py
│   │   ├── list_profiles/
│   │   │   ├── __init__.py
│   │   │   └── test_list_profiles_handler.py
│   │   └── set_username/
│   │       ├── __init__.py
│   │       └── test_set_username_handler.py
│   └── domain/
│       ├── __init__.py
│       ├── test_profile_entity.py              ← NEW
│       └── test_username.py                    ← NEW
├── shared/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── test_entity_base.py                 ← renamed from entities/test_base.py
│   │   ├── test_value_object_base.py           ← renamed from value_objects/test_base.py
│   │   └── authorization/
│   │       ├── __init__.py
│   │       ├── permission_stubs.py             ← moved
│   │       ├── test_authorize.py               ← moved
│   │       ├── test_composite.py               ← moved
│   │       └── test_permissions.py             ← moved
│   └── infrastructure/
│       ├── __init__.py
│       ├── conftest.py                         ← moved from infrastructure/
│       ├── test_password_hasher_bcrypt.py       ← moved
│       ├── test_cfg_database.py                ← moved from setup/
│       ├── test_cfg_loader.py                  ← moved
│       ├── test_cfg_logs.py                    ← moved
│       └── test_cfg_security.py                ← moved
└── factories/
    ├── __init__.py
    ├── account_entity.py                       ← renamed from user_entity.py
    ├── profile_entity.py                       ← NEW
    ├── named_entity.py
    ├── tagged_entity.py
    ├── settings_data.py
    └── value_objects.py
```

## File Rename/Move Mapping

| Old path | New path |
|---|---|
| `application/log_in/` | `account/application/log_in/` |
| `application/refresh_token/` | `account/application/refresh_token/` |
| `application/authz_service/` | `shared/domain/authorization/` |
| `domain/entities/test_base.py` | `shared/domain/test_entity_base.py` |
| `domain/enums/test_user_role.py` | `account/domain/test_account_role.py` |
| `domain/services/test_user.py` | `account/domain/test_account_entity.py` |
| `domain/services/conftest.py` | `account/domain/conftest.py` |
| `domain/services/mock_types.py` | `account/domain/mock_types.py` |
| `domain/value_objects/test_base.py` | `shared/domain/test_value_object_base.py` |
| `domain/value_objects/test_raw_password.py` | `account/domain/test_raw_password.py` |
| `domain/value_objects/test_username.py` | `account/domain/test_email.py` |
| `infrastructure/` | `shared/infrastructure/` |
| `setup/` | `shared/infrastructure/` |
| `factories/user_entity.py` | `factories/account_entity.py` |

## Import Updates Required

All moved test files need their factory imports updated:
- `tests.app.unit.factories.user_entity` → `tests.app.unit.factories.account_entity`
- `tests.app.unit.domain.services.mock_types` → `tests.app.unit.account.domain.mock_types`

## Test Pattern for Handler Tests

Follow the established pattern from `test_log_in_handler.py`:

```python
from typing import cast
from unittest.mock import AsyncMock, create_autospec
from uuid import UUID

import pytest

# ... handler-specific imports ...

@pytest.mark.asyncio
async def test_<behavior_description>() -> None:
    # 1. Create mocks with create_autospec
    dep = create_autospec(SomeProtocol, instance=True)

    # 2. Set return values
    cast(AsyncMock, dep.method).return_value = value

    # 3. Instantiate SUT
    sut = SomeHandler(dep=cast(SomeProtocol, dep))

    # 4. Execute
    result = await sut.execute(command)

    # 5. Assert results + mock interactions
    assert result.field == expected
    cast(AsyncMock, dep.method).assert_awaited_once()
```

For handlers that depend on `CurrentAccountHandler`, mock it:
```python
current_account_handler = create_autospec(CurrentAccountHandler, instance=True)
cast(AsyncMock, current_account_handler.get_current_account).return_value = admin_account
```

## New Factory: Profile Entity

```python
# factories/profile_entity.py
from core.domain.profile.entity import Profile
from core.domain.profile.value_objects import ProfileId, Username
from shared.domain.account_id import AccountId

def create_profile(
    profile_id: ProfileId = ...,
    account_id: AccountId = ...,
    username: Username | None = None,
) -> Profile:
    ...
```

## Test Case Coverage per Handler

### CurrentAccountHandler
- Returns active account on happy path
- Raises AuthorizationError + revokes access when account is None
- Raises AuthorizationError + revokes access when account is inactive
- Forwards for_update to repository

### ActivateAccountHandler
- Happy path: UoW committed, events dispatched
- Already active: UoW NOT committed, events dispatched (empty list)
- USER caller: AuthorizationError (CanManageRole)
- Target not found: AccountNotFoundByIdError
- ADMIN targeting ADMIN: AuthorizationError (CanManageSubordinate)

### DeactivateAccountHandler
- Happy path: UoW committed, access revoked, events dispatched
- Already inactive: UoW NOT committed, access still revoked
- USER caller: AuthorizationError
- Target not found: AccountNotFoundByIdError
- ADMIN targeting ADMIN: AuthorizationError

### GrantAdminHandler
- Happy path (SUPER_ADMIN promotes USER to ADMIN): UoW committed
- Already ADMIN: UoW NOT committed
- ADMIN caller: AuthorizationError (can't manage ADMIN role)
- Target not found: AccountNotFoundByIdError

### RevokeAdminHandler
- Happy path (SUPER_ADMIN demotes ADMIN to USER): UoW committed
- Already USER: UoW NOT committed
- ADMIN caller: AuthorizationError
- Target not found: AccountNotFoundByIdError

### CreateAccountHandler
- Happy path: returns CreateAccountResponse with correct ID
- USER caller: AuthorizationError
- ADMIN creating ADMIN: AuthorizationError
- EmailAlreadyExistsError propagated

### SignUpHandler
- Happy path (unauthenticated): returns SignUpResponse
- Already authenticated: AlreadyAuthenticatedError
- CurrentAccountHandler raises AuthorizationError: swallowed, sign-up proceeds
- EmailAlreadyExistsError propagated

### ChangePasswordHandler
- Happy path: UoW committed
- Same password: AuthenticationChangeError
- Wrong current password: ReAuthenticationError
- for_update=True forwarded to CurrentAccountHandler

### SetAccountPasswordHandler
- Happy path: UoW committed, events dispatched
- USER caller: AuthorizationError
- Target not found: AccountNotFoundByIdError
- ADMIN targeting ADMIN: AuthorizationError

### ListAccountsHandler
- Happy path: returns repo result
- USER caller: AuthorizationError
- Pagination/sorting forwarded to repo

### GetMyProfileHandler
- Happy path with username
- Happy path without username (None)
- Profile not found: ProfileNotFoundByAccountIdError

### ListProfilesHandler
- Happy path (ADMIN): returns repo result
- Happy path (SUPER_ADMIN): returns repo result
- Account not found: AuthorizationError
- USER role: AuthorizationError

### SetUsernameHandler
- Happy path: UoW committed, events dispatched
- Profile not found: ProfileNotFoundByAccountIdError
- for_update=True forwarded to repo

## New Domain Tests

### Profile Entity
- `Profile.create()` registers ProfileCreated event
- `set_username()` changes username and registers UsernameChanged event
- `set_username()` with same username returns False, no event
- `set_username()` from None to a value works correctly

### Username Value Object
- Valid usernames accepted (min length, max length, mixed chars)
- Too short: DomainTypeError
- Too long: DomainTypeError
- Starts with special char: DomainTypeError
- Ends with special char: DomainTypeError
- Contains disallowed chars: DomainTypeError
- Consecutive specials: DomainTypeError
