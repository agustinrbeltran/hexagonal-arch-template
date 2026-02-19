# Tasks: Fix Unit Test Structure

## Phase 1: Restructure directories and rename files

- [ ] 1.1 Create new directory skeleton under `tests/app/unit/` (`account/`, `core/`, `shared/` with all subdirectories and `__init__.py` files)
- [ ] 1.2 Move and rename `factories/user_entity.py` → `factories/account_entity.py`; update internal references
- [ ] 1.3 Create `factories/profile_entity.py` with `create_profile()` and `create_profile_id()` factories
- [ ] 1.4 Update `factories/value_objects.py` to add profile-related VO factories (`create_profile_id`, `create_username`)
- [ ] 1.5 Move existing handler tests: `application/log_in/` → `account/application/log_in/`, `application/refresh_token/` → `account/application/refresh_token/`
- [ ] 1.6 Move authorization tests: `application/authz_service/` → `shared/domain/authorization/`
- [ ] 1.7 Move and rename domain entity tests: `domain/entities/test_base.py` → `shared/domain/test_entity_base.py`
- [ ] 1.8 Move and rename domain VO tests: `domain/value_objects/test_base.py` → `shared/domain/test_value_object_base.py`
- [ ] 1.9 Move and rename account domain tests: `test_user_role.py` → `account/domain/test_account_role.py`, `test_user.py` → `account/domain/test_account_entity.py`, `test_username.py` → `account/domain/test_email.py`, `test_raw_password.py` → `account/domain/test_raw_password.py`, `conftest.py` + `mock_types.py` → `account/domain/`
- [ ] 1.10 Move infrastructure tests: `infrastructure/` → `shared/infrastructure/`
- [ ] 1.11 Move setup tests: `setup/` → `shared/infrastructure/`
- [ ] 1.12 Update all import paths in moved files (factory imports, mock_types imports)
- [ ] 1.13 Delete old empty directories after all moves are complete
- [ ] 1.14 Run existing tests to confirm nothing broke: `PYTHONPATH=src python -m pytest tests/ -x -q`

## Phase 2: Add missing account handler tests

- [ ] 2.1 Write `account/application/current_account/test_current_account_handler.py` (4 test cases)
- [ ] 2.2 Write `account/application/activate_account/test_activate_account_handler.py` (5 test cases)
- [ ] 2.3 Write `account/application/deactivate_account/test_deactivate_account_handler.py` (5 test cases)
- [ ] 2.4 Write `account/application/grant_admin/test_grant_admin_handler.py` (4 test cases)
- [ ] 2.5 Write `account/application/revoke_admin/test_revoke_admin_handler.py` (4 test cases)
- [ ] 2.6 Write `account/application/create_account/test_create_account_handler.py` (4 test cases)
- [ ] 2.7 Write `account/application/sign_up/test_sign_up_handler.py` (4 test cases)
- [ ] 2.8 Write `account/application/change_password/test_change_password_handler.py` (4 test cases)
- [ ] 2.9 Write `account/application/set_account_password/test_set_account_password_handler.py` (4 test cases)
- [ ] 2.10 Write `account/application/list_accounts/test_list_accounts_handler.py` (3 test cases)
- [ ] 2.11 Run account handler tests to verify: `PYTHONPATH=src python -m pytest tests/app/unit/account/application/ -x -q`

## Phase 3: Add missing core (Profile) tests

- [ ] 3.1 Write `core/domain/test_profile_entity.py` (4 test cases: create event, set_username changed, set_username same, set_username from None)
- [ ] 3.2 Write `core/domain/test_username.py` (7 test cases: valid, too short, too long, bad start, bad end, bad chars, consecutive specials)
- [ ] 3.3 Write `core/application/get_my_profile/test_get_my_profile_handler.py` (3 test cases)
- [ ] 3.4 Write `core/application/list_profiles/test_list_profiles_handler.py` (4 test cases)
- [ ] 3.5 Write `core/application/set_username/test_set_username_handler.py` (3 test cases)
- [ ] 3.6 Run core tests to verify: `PYTHONPATH=src python -m pytest tests/app/unit/core/ -x -q`

## Phase 4: Final validation

- [ ] 4.1 Run full test suite: `PYTHONPATH=src python -m pytest tests/ -x -q`
- [ ] 4.2 Verify test count increased from ~132 to expected total (~200+)
