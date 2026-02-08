## 1. Domain Shared Foundation

- [ ] 1.1 Create `src/domain/` package and `src/domain/shared/` subpackage with `__init__.py` files
- [ ] 1.2 Create `domain/shared/domain_event.py` — DomainEvent base class with `event_id`, `occurred_at`, `event_type`
- [ ] 1.3 Create `domain/shared/aggregate_root.py` — AggregateRoot[ID] extending Entity with `_events` list, `_register_event()`, `collect_events()`
- [ ] 1.4 Move/refactor `domain/shared/entity.py` — Entity[ID] base class (adapt from existing `src/common/domain/core/entities/base.py`)
- [ ] 1.5 Move/refactor `domain/shared/value_object.py` — ValueObject base class (adapt from existing `src/common/domain/core/value_objects/base.py`)
- [ ] 1.6 Create `domain/shared/errors.py` — DomainError, DomainTypeError, NotFoundError, AuthorizationError (consolidate from existing scattered error modules)

## 2. User Aggregate (Domain Layer)

- [ ] 2.1 Create `src/domain/user/` package with `__init__.py`
- [ ] 2.2 Create `domain/user/entity.py` — User class extending AggregateRoot[UserId] with business methods that register domain events
- [ ] 2.3 Create `domain/user/value_objects.py` — Move UserId, Username, UserPasswordHash, RawPassword from `src/features/user/domain/core/vo/`
- [ ] 2.4 Create `domain/user/events.py` — UserCreated, UserActivated, UserDeactivated, UserRoleChanged, UserPasswordChanged
- [ ] 2.5 Create `domain/user/repository.py` — UserRepository protocol (move from `src/features/user/domain/port/outbound/user_repository.py`)
- [ ] 2.6 Create `domain/user/services.py` — Move UserService with authorization/role-hierarchy logic from `src/features/user/domain/core/service/`
- [ ] 2.7 Create `domain/user/errors.py` — Move user-specific errors from `src/features/user/domain/core/exceptions/`
- [ ] 2.8 Move UserRole enum and role_hierarchy to `domain/user/enums.py`
- [ ] 2.9 Move outbound port protocols (PasswordHasher, IdentityProvider, AccessRevoker) to `domain/user/ports.py`

## 3. AuthSession Aggregate (Domain Layer)

- [ ] 3.1 Create `src/domain/auth_session/` package with `__init__.py`
- [ ] 3.2 Create `domain/auth_session/entity.py` — AuthSession extending AggregateRoot with session lifecycle methods
- [ ] 3.3 Create `domain/auth_session/events.py` — SessionCreated, SessionExpired, SessionRevoked
- [ ] 3.4 Create `domain/auth_session/gateway.py` — AuthSessionGateway protocol (move from `src/features/account/domain/port/outbound/`)
- [ ] 3.5 Create `domain/auth_session/errors.py` — SessionNotFoundError, SessionExpiredError
- [ ] 3.6 Move AuthSessionService to `domain/auth_session/services.py`
- [ ] 3.7 Move remaining outbound port protocols (AuthSessionTransport, AuthSessionTransactionManager) to `domain/auth_session/ports.py`

## 4. Application Layer — Shared

- [ ] 4.1 Create `src/application/` package and `src/application/shared/` subpackage
- [ ] 4.2 Create `application/shared/unit_of_work.py` — UnitOfWork protocol with commit() and rollback()
- [ ] 4.3 Create `application/shared/event_dispatcher.py` — EventDispatcher protocol

## 5. Application Layer — User Use Cases

- [ ] 5.1 Create `application/create_user/` — command.py (CreateUserCommand), handler.py (CreateUserHandler), port.py (CreateUserUseCase protocol)
- [ ] 5.2 Create `application/activate_user/` — command.py, handler.py, port.py
- [ ] 5.3 Create `application/deactivate_user/` — command.py, handler.py, port.py
- [ ] 5.4 Create `application/grant_admin/` — command.py, handler.py, port.py
- [ ] 5.5 Create `application/revoke_admin/` — command.py, handler.py, port.py
- [ ] 5.6 Create `application/set_user_password/` — command.py, handler.py, port.py
- [ ] 5.7 Create `application/list_users/` — query.py (ListUsersQuery), handler.py, port.py
- [ ] 5.8 Create `application/current_user/` — query.py, handler.py, port.py

## 6. Application Layer — Account Use Cases

- [ ] 6.1 Create `application/sign_up/` — command.py (SignUpCommand), handler.py (SignUpHandler), port.py (SignUpUseCase protocol)
- [ ] 6.2 Create `application/log_in/` — command.py, handler.py, port.py
- [ ] 6.3 Create `application/log_out/` — command.py, handler.py, port.py
- [ ] 6.4 Create `application/change_password/` — command.py, handler.py, port.py

## 7. Infrastructure — Persistence Adapters

- [ ] 7.1 Create `src/infrastructure/` package and `src/infrastructure/persistence/` subpackage
- [ ] 7.2 Move SQLAlchemy mapper registry to `infrastructure/persistence/registry.py`
- [ ] 7.3 Move User table mapping to `infrastructure/persistence/mappers/user.py`
- [ ] 7.4 Move AuthSession table mapping to `infrastructure/persistence/mappers/auth_session.py`
- [ ] 7.5 Move SqlaUserRepository to `infrastructure/persistence/sqla_user_repository.py` — implement domain UserRepository protocol
- [ ] 7.6 Move SqlaAuthSessionGateway to `infrastructure/persistence/sqla_auth_session_gateway.py` — implement domain AuthSessionGateway protocol
- [ ] 7.7 Create `infrastructure/persistence/sqla_unit_of_work.py` — implement UnitOfWork protocol using SQLAlchemy async session
- [ ] 7.8 Move session factory types (MainAsyncSession, AuthAsyncSession) to `infrastructure/persistence/types_.py`
- [ ] 7.9 Move transaction manager adapters to `infrastructure/persistence/`

## 8. Infrastructure — HTTP Driver Adapters

- [ ] 8.1 Create `src/infrastructure/http/` subpackage
- [ ] 8.2 Move all user REST controllers to `infrastructure/http/controllers/user/` — update to depend on application ports
- [ ] 8.3 Move all account REST controllers to `infrastructure/http/controllers/account/` — update to depend on application ports
- [ ] 8.4 Move routers (root_router, api_v1_router, user_router, account_router) to `infrastructure/http/routers/`
- [ ] 8.5 Move error handlers and translators to `infrastructure/http/errors/`
- [ ] 8.6 Move health check controller to `infrastructure/http/controllers/health.py`
- [ ] 8.7 Move ASGI middleware and JWT/cookie adapters to `infrastructure/http/middleware/`

## 9. Infrastructure — Security Adapters

- [ ] 9.1 Create `src/infrastructure/security/` subpackage
- [ ] 9.2 Move BcryptPasswordHasher to `infrastructure/security/password_hasher_bcrypt.py`
- [ ] 9.3 Move JWT access token processor to `infrastructure/security/access_token_processor_jwt.py`
- [ ] 9.4 Move cookie session transport to `infrastructure/security/session_transport_jwt_cookie.py`
- [ ] 9.5 Move identity provider adapter to `infrastructure/security/identity_provider.py`
- [ ] 9.6 Move access revoker adapter to `infrastructure/security/access_revoker.py`

## 10. Infrastructure — Config & DI

- [ ] 10.1 Create `src/infrastructure/config/` and `src/infrastructure/config/di/` subpackages
- [ ] 10.2 Move settings models (AppSettings, PostgresSettings, SecuritySettings, etc.) to `infrastructure/config/settings/`
- [ ] 10.3 Reorganize Dishka providers into `infrastructure/config/di/domain.py`, `application.py`, `infrastructure.py`, `settings.py`
- [ ] 10.4 Create `infrastructure/config/di/provider_registry.py` — composition root that wires all providers
- [ ] 10.5 Move app_factory.py to `infrastructure/config/app_factory.py` — update all imports

## 11. Domain Events Infrastructure

- [ ] 11.1 Create `infrastructure/events/in_process_dispatcher.py` — InProcessEventDispatcher implementing EventDispatcher protocol
- [ ] 11.2 Wire event dispatcher into DI container
- [ ] 11.3 Update use case handlers to call `collect_events()` on aggregates after commit and dispatch events

## 12. Entry Point & Cleanup

- [ ] 12.1 Update `src/run.py` (or create `src/main.py`) to import from new infrastructure paths
- [ ] 12.2 Remove old `src/features/`, `src/common/`, `src/setup/` directories after all code is migrated
- [ ] 12.3 Update `pyproject.toml` if any path-based configuration references old structure
- [ ] 12.4 Update all test imports to match new module paths
- [ ] 12.5 Run full test suite and verify all tests pass
- [ ] 12.6 Verify all HTTP endpoints return identical responses (API contract check)
- [ ] 12.7 Verify domain layer has zero framework imports (dependency rule check)
