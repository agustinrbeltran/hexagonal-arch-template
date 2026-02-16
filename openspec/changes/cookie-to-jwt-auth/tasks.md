## 1. Database Migration

- [x] 1.1 Create migration to rename `auth_sessions` table to `refresh_tokens`

## 2. Domain Layer — RefreshToken Aggregate

- [x] 2.1 Create `domain/refresh_token/entity.py` with `RefreshToken` dataclass (id_, user_id, expiration)
- [x] 2.2 Create `domain/refresh_token/errors.py` with `RefreshTokenNotFoundError` and `RefreshTokenExpiredError`
- [x] 2.3 Create `domain/refresh_token/repository.py` with `RefreshTokenRepository` protocol (add, get_by_id, delete, delete_all_for_user)
- [x] 2.4 Create `domain/refresh_token/services.py` with `RefreshTokenService` (issue_token_pair, refresh, revoke_all_for_user) plus `RefreshTokenIdGenerator` protocol
- [x] 2.5 Delete `domain/auth_session/` directory entirely (entity, services, gateway, ports, errors, events)

## 3. Infrastructure — Persistence Adapters

- [x] 3.1 Create `infrastructure/persistence/mappers/refresh_token.py` with imperative SQLAlchemy mapping for `refresh_tokens` table
- [x] 3.2 Create `infrastructure/persistence/sqla_refresh_token_repository.py` implementing `RefreshTokenRepository`
- [x] 3.3 Delete `infrastructure/persistence/mappers/auth_session.py`
- [x] 3.4 Delete `infrastructure/persistence/sqla_auth_session_gateway.py`
- [x] 3.5 Delete `infrastructure/persistence/sqla_auth_session_transaction_manager.py`
- [x] 3.6 Update `infrastructure/persistence/mappers/__init__.py` to import refresh_token mapper instead of auth_session

## 4. Infrastructure — Security Adapters

- [x] 4.1 Rewrite `infrastructure/security/access_token_processor_jwt.py` — payload changes to `{sub, exp, iat}`, add `encode(user_id, expiration)` and `decode_user_id(token)` methods
- [x] 4.2 Rewrite `infrastructure/security/identity_provider.py` — `JwtBearerIdentityProvider` reads `Authorization: Bearer` header, decodes JWT, returns UserId
- [x] 4.3 Rewrite `infrastructure/security/access_revoker.py` — `RefreshTokenAccessRevoker` calls `RefreshTokenService.revoke_all_for_user()`
- [x] 4.4 Create `infrastructure/security/refresh_token_id_generator.py` with `StrRefreshTokenIdGenerator` using `secrets.token_urlsafe(32)`
- [x] 4.5 Delete `infrastructure/security/session_transport_jwt_cookie.py`
- [x] 4.6 Delete `infrastructure/security/auth_session_id_generator.py`
- [x] 4.7 Delete `infrastructure/security/auth_session_timer.py`

## 5. Infrastructure — HTTP Layer

- [x] 5.1 Create token response model (dataclass or Pydantic model) with `access_token`, `refresh_token`, `token_type`, `expires_in`
- [x] 5.2 Rewrite `infrastructure/http/controllers/account/log_in.py` — return 200 + JSON token pair response, remove AlreadyAuthenticatedError handling
- [x] 5.3 Create `infrastructure/http/controllers/account/refresh.py` — POST /refresh endpoint returning token pair
- [x] 5.4 Delete `infrastructure/http/controllers/account/log_out.py`
- [x] 5.5 Update `infrastructure/http/routers/account_router.py` — remove logout route, add refresh route
- [x] 5.6 Replace `openapi_marker.py` cookie scheme with `HTTPBearer` scheme
- [x] 5.7 Delete `infrastructure/http/middleware/asgi_middleware.py`
- [x] 5.8 Delete `infrastructure/http/middleware/constants.py`
- [x] 5.9 Delete `infrastructure/http/middleware/cookie_params.py`
- [x] 5.10 Remove `ASGIAuthMiddleware` from app factory

## 6. Application Layer

- [x] 6.1 Rewrite `application/log_in/handler.py` — remove CurrentUserHandler dependency, replace AuthSessionService with RefreshTokenService, return token pair
- [x] 6.2 Update `application/log_in/port.py` — change return type from None to token pair
- [x] 6.3 Create `application/refresh_token/command.py` with `RefreshTokenCommand(refresh_token: str)`
- [x] 6.4 Create `application/refresh_token/handler.py` with `RefreshTokenHandler`
- [x] 6.5 Create `application/refresh_token/port.py` with `RefreshTokenUseCase` ABC
- [x] 6.6 Delete `application/log_out/` directory entirely

## 7. Configuration & DI

- [x] 7.1 Update `infrastructure/config/settings/security.py` — replace `SESSION_TTL_MIN` and `SESSION_REFRESH_THRESHOLD` with `ACCESS_TOKEN_EXPIRY_MIN` and `REFRESH_TOKEN_EXPIRY_DAYS`, remove `CookiesSettings`
- [x] 7.2 Update `config/local/config.toml` and `.secrets.toml` — update `[security.auth]` keys, remove `[security.cookies]`
- [x] 7.3 Update `infrastructure/config/di/application.py` — remove log_out provider, add refresh_token provider, update identity provider and access revoker bindings
- [x] 7.4 Update `infrastructure/config/di/infrastructure.py` — remove AuthSession* providers, add RefreshToken* providers, remove CookieParams/EntrypointProvider cookie-related bindings
- [x] 7.5 Update `infrastructure/config/di/domain.py` if it references AuthSessionService

## 8. Cleanup & Verification

- [x] 8.1 Remove any remaining imports of deleted modules across the codebase
- [x] 8.2 Run tests — ensure all existing tests pass
- [x] 8.3 Verify login endpoint returns 200 + JSON with token pair
- [x] 8.4 Verify refresh endpoint works with token rotation
- [x] 8.5 Verify authenticated endpoints accept Bearer token
- [x] 8.6 Verify deactivate-user revokes refresh tokens
