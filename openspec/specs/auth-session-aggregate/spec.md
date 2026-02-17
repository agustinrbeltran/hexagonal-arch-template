## REMOVED Requirements

### Requirement: AuthSession aggregate root at domain/auth_session/entity.py
**Reason**: Replaced by `RefreshToken` dataclass at `infrastructure/security/refresh_token.py`. Server-side sessions are eliminated in favor of stateless JWT access tokens + server-side refresh tokens.
**Migration**: All code referencing `AuthSession` must reference `RefreshToken` instead. The `domain/auth_session/` directory is deleted entirely.

### Requirement: AuthSession domain events at domain/auth_session/events.py
**Reason**: Session lifecycle events (`SessionCreated`, `SessionExpired`, `SessionRevoked`) are no longer relevant. Refresh token operations do not emit domain events.
**Migration**: Remove all references to `SessionCreated`, `SessionExpired`, `SessionRevoked`. Delete `domain/auth_session/events.py`.

### Requirement: AuthSession gateway port at domain/auth_session/gateway.py
**Reason**: Replaced by `RefreshTokenRepository` protocol at `infrastructure/security/refresh_token_repository.py`.
**Migration**: All code depending on `AuthSessionGateway` must depend on `RefreshTokenRepository` instead.

### Requirement: AuthSession domain errors at domain/auth_session/errors.py
**Reason**: Replaced by `RefreshTokenNotFoundError` and `RefreshTokenExpiredError` at `infrastructure/security/errors.py`.
**Migration**: All code catching `SessionNotFoundError` or `SessionExpiredError` must catch the new refresh token errors instead.
