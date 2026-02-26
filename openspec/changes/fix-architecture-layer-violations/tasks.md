## 1. Move register_event to shared domain

- [ ] 1.1 Create `shared/domain/event_registry.py` with `register_event` decorator and `_event_type_registry` dict (moved from `shared/infrastructure/events/registry.py`)
- [ ] 1.2 Update `shared/infrastructure/events/registry.py` to import `register_event` and `_event_type_registry` from `shared.domain.event_registry` instead of defining them locally
- [ ] 1.3 Update `account/domain/account/events.py` to import `register_event` from `shared.domain.event_registry`
- [ ] 1.4 Update `core/domain/profile/events.py` to import `register_event` from `shared.domain.event_registry`
- [ ] 1.5 Update any tests that import `register_event` from the old path

## 2. Replace CurrentAccountHandler with CurrentAccountUseCase in handlers

- [ ] 2.1 Update `sign_up/handler.py`: change import and type hint from `CurrentAccountHandler` to `CurrentAccountUseCase`
- [ ] 2.2 Update `create_account/handler.py`: change import and type hint from `CurrentAccountHandler` to `CurrentAccountUseCase`
- [ ] 2.3 Update `activate_account/handler.py`: change import and type hint from `CurrentAccountHandler` to `CurrentAccountUseCase`
- [ ] 2.4 Update `deactivate_account/handler.py`: change import and type hint from `CurrentAccountHandler` to `CurrentAccountUseCase`
- [ ] 2.5 Update `grant_admin/handler.py`: change import and type hint from `CurrentAccountHandler` to `CurrentAccountUseCase`
- [ ] 2.6 Update `revoke_admin/handler.py`: change import and type hint from `CurrentAccountHandler` to `CurrentAccountUseCase`
- [ ] 2.7 Update `list_accounts/handler.py`: change import and type hint from `CurrentAccountHandler` to `CurrentAccountUseCase`
- [ ] 2.8 Update `set_account_password/handler.py`: change import and type hint from `CurrentAccountHandler` to `CurrentAccountUseCase`
- [ ] 2.9 Update `change_password/handler.py`: change import and type hint from `CurrentAccountHandler` to `CurrentAccountUseCase`
- [ ] 2.10 Remove `provide_all(CurrentAccountHandler)` line and its comment from `shared/infrastructure/config/di/application.py`
- [ ] 2.11 Update any tests that mock or reference `CurrentAccountHandler` as a dependency type

## 3. Introduce AuthorizationGuard port and implementation

- [ ] 3.1 Create `shared/domain/ports/authorization_guard.py` with `AuthorizationGuard` Protocol defining `async def require_admin(self) -> None`
- [ ] 3.2 Create `account/infrastructure/security/authorization_guard.py` with `AccountAuthorizationGuard` implementing the protocol using `IdentityProvider` and `AccountRepository`
- [ ] 3.3 Register `AccountAuthorizationGuard` as `AuthorizationGuard` provider in `shared/infrastructure/config/di/application.py`
- [ ] 3.4 Refactor `core/application/list_profiles/handler.py` to depend on `AuthorizationGuard` instead of `AccountRepository` and `AccountRole`
- [ ] 3.5 Update tests for `ListProfilesHandler` to mock `AuthorizationGuard` instead of `AccountRepository`

## 4. Verification

- [ ] 4.1 Run `make code.check` (lint + tests) and fix any failures
