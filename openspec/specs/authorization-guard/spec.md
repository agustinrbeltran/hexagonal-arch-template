## ADDED Requirements

### Requirement: AuthorizationGuard port in shared domain
The system SHALL provide an `AuthorizationGuard` protocol in `shared/domain/ports/authorization_guard.py` with an async method `require_admin() -> None`. When the current user lacks admin-level access, the method SHALL raise `AuthorizationError`. This port allows any bounded context to enforce admin authorization without importing another context's domain types.

#### Scenario: Admin user passes the guard
- **WHEN** `require_admin()` is called and the current user has `ADMIN` or `SUPER_ADMIN` role
- **THEN** the method returns without raising

#### Scenario: Non-admin user is rejected
- **WHEN** `require_admin()` is called and the current user has `MEMBER` role
- **THEN** `AuthorizationError` is raised

#### Scenario: Unknown or inactive user is rejected
- **WHEN** `require_admin()` is called and the current user's account is not found or is inactive
- **THEN** `AuthorizationError` is raised

### Requirement: AccountAuthorizationGuard implementation
The system SHALL provide an `AccountAuthorizationGuard` class in `account/infrastructure/security/` that implements `AuthorizationGuard`. It SHALL depend on `IdentityProvider` and `AccountRepository` to resolve the current user's account and check their role. It SHALL NOT be imported by any application or domain layer code directly — it is wired via the DI container.

#### Scenario: Implementation resolves account and checks role
- **WHEN** `AccountAuthorizationGuard.require_admin()` is called
- **THEN** it obtains the account ID from `IdentityProvider`, fetches the account from `AccountRepository`, and checks that the role is `ADMIN` or `SUPER_ADMIN`

#### Scenario: DI container wires implementation to port
- **WHEN** inspecting the DI container configuration
- **THEN** `AccountAuthorizationGuard` is provided as the `AuthorizationGuard` port
