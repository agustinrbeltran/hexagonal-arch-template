## REMOVED Requirements

### Requirement: Security adapters under infrastructure/security/
**Reason**: The cookie-based session transport (`JwtCookieAuthSessionTransport`), session ID generator (`StrAuthSessionIdGenerator`), session timer (`UtcAuthSessionTimer`), and session-based identity provider (`AuthSessionIdentityProvider`) and access revoker (`AuthSessionAccessRevoker`) are removed. Replaced by JWT bearer identity provider and refresh token access revoker.
**Migration**: Delete `session_transport_jwt_cookie.py`, `auth_session_id_generator.py`, `auth_session_timer.py`. Replace `identity_provider.py` and `access_revoker.py` implementations.

## ADDED Requirements

### Requirement: JwtBearerIdentityProvider at infrastructure/security/identity_provider.py
The system SHALL implement `IdentityProvider` with a `JwtBearerIdentityProvider` that reads the `Authorization: Bearer <token>` header from the current request, decodes the JWT using `JwtAccessTokenProcessor`, extracts the `sub` claim, and returns it as a `UserId`. This provider MUST NOT perform any database queries.

#### Scenario: Extracts user_id from Bearer token
- **WHEN** a request has `Authorization: Bearer <valid-jwt>` header
- **THEN** `get_current_user_id()` returns the `UserId` from the JWT's `sub` claim

#### Scenario: Raises authentication error for missing header
- **WHEN** a request has no `Authorization` header
- **THEN** `get_current_user_id()` raises an authentication error

#### Scenario: Raises authentication error for invalid token
- **WHEN** a request has an invalid or expired Bearer token
- **THEN** `get_current_user_id()` raises an authentication error

### Requirement: RefreshTokenAccessRevoker at infrastructure/security/access_revoker.py
The system SHALL implement `AccessRevoker` with a `RefreshTokenAccessRevoker` that calls `RefreshTokenService.revoke_all_for_user(user_id)` to delete all refresh tokens for a user.

#### Scenario: Revokes all refresh tokens for a user
- **WHEN** `remove_all_user_access(user_id)` is called
- **THEN** all refresh tokens for that user are deleted from the database

### Requirement: JwtAccessTokenProcessor encodes/decodes standard claims
The `JwtAccessTokenProcessor` at `infrastructure/security/access_token_processor_jwt.py` SHALL encode JWTs with `{sub: str(user_id), exp: int, iat: int}` and decode them by extracting the `sub` claim as a user ID string. The processor MUST replace the previous `auth_session_id`-based payload.

#### Scenario: Encode produces JWT with sub, exp, iat
- **WHEN** `encode(user_id, expiration)` is called
- **THEN** the resulting JWT contains `sub`, `exp`, and `iat` claims only

#### Scenario: Decode extracts user_id from sub claim
- **WHEN** `decode_user_id(token)` is called with a valid JWT
- **THEN** it returns the string from the `sub` claim

#### Scenario: Decode returns None for invalid token
- **WHEN** `decode_user_id(token)` is called with an expired or tampered JWT
- **THEN** it returns `None`

### Requirement: RefreshToken persistence adapter at infrastructure/persistence/
The system SHALL provide `SqlaRefreshTokenRepository` implementing `RefreshTokenRepository`, plus an imperative SQLAlchemy mapper for the `refresh_tokens` table. The table schema MUST have columns: `id` (String PK), `user_id` (UUID FK to users), `expiration` (DateTime with timezone).

#### Scenario: SqlaRefreshTokenRepository implements the port
- **WHEN** `SqlaRefreshTokenRepository` is inspected
- **THEN** it satisfies the `RefreshTokenRepository` protocol with `add`, `get_by_id`, `delete`, `delete_all_for_user`

#### Scenario: Imperative mapper maps RefreshToken to refresh_tokens table
- **WHEN** the SQLAlchemy mapper registry is initialized
- **THEN** `RefreshToken` is mapped to the `refresh_tokens` table

### Requirement: ASGI cookie middleware removed
The system SHALL NOT include the `ASGIAuthMiddleware`. The app factory MUST NOT register any cookie-handling middleware. The `infrastructure/http/middleware/` cookie-related modules (`asgi_middleware.py`, `constants.py`, `cookie_params.py`) MUST be deleted.

#### Scenario: App factory does not add cookie middleware
- **WHEN** `create_web_app()` is called
- **THEN** no `ASGIAuthMiddleware` is added to the application

### Requirement: Login controller returns 200 with token pair
The login controller at `infrastructure/http/controllers/account/log_in.py` SHALL return HTTP 200 with a JSON response model containing `access_token`, `refresh_token`, `token_type`, and `expires_in`. It MUST NOT return 204 or set any cookies.

#### Scenario: Login endpoint returns JSON token response
- **WHEN** `POST /api/v1/account/login` succeeds
- **THEN** response is `200 OK` with JSON body `{access_token, refresh_token, token_type, expires_in}`

### Requirement: Refresh controller at infrastructure/http/controllers/account/
The system SHALL provide a refresh controller handling `POST /api/v1/account/refresh`. It MUST accept JSON body with `refresh_token` field, call the `RefreshTokenUseCase`, and return the same token pair response model as login.

#### Scenario: Refresh endpoint returns new token pair
- **WHEN** `POST /api/v1/account/refresh` is called with a valid refresh token
- **THEN** response is `200 OK` with JSON body `{access_token, refresh_token, token_type, expires_in}`

#### Scenario: Refresh endpoint returns 401 for invalid token
- **WHEN** `POST /api/v1/account/refresh` is called with an invalid token
- **THEN** response is `401 Unauthorized`

### Requirement: Logout controller and route removed
The system SHALL NOT provide a logout endpoint. The `DELETE /api/v1/account/logout` route MUST be removed from the account router.

#### Scenario: Logout route does not exist
- **WHEN** the API route table is inspected
- **THEN** there is no `DELETE /api/v1/account/logout` route

### Requirement: DI providers updated for new auth architecture
The Dishka DI providers MUST be updated to: remove all `AuthSession*` provider bindings, add `RefreshTokenService`, `RefreshTokenRepository`, `RefreshTokenIdGenerator` bindings, replace `AuthSessionIdentityProvider` with `JwtBearerIdentityProvider`, replace `AuthSessionAccessRevoker` with `RefreshTokenAccessRevoker`, remove `AuthSessionTransport`, `AuthSessionTransactionManager`, `CookieParams` providers.

#### Scenario: DI container provides RefreshTokenService
- **WHEN** the Dishka container resolves `RefreshTokenService`
- **THEN** it returns a fully wired instance

#### Scenario: DI container provides JwtBearerIdentityProvider as IdentityProvider
- **WHEN** the Dishka container resolves `IdentityProvider`
- **THEN** it returns a `JwtBearerIdentityProvider` instance

### Requirement: Security settings updated
The `AuthSettings` model MUST include `ACCESS_TOKEN_EXPIRY_MIN` (int, default 15) and `REFRESH_TOKEN_EXPIRY_DAYS` (int, default 7) replacing `SESSION_TTL_MIN` and `SESSION_REFRESH_THRESHOLD`. The `CookiesSettings` model MUST be removed.

#### Scenario: AuthSettings contains token expiry fields
- **WHEN** `AuthSettings` is inspected
- **THEN** it has `JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRY_MIN`, and `REFRESH_TOKEN_EXPIRY_DAYS` fields

#### Scenario: CookiesSettings is removed
- **WHEN** the settings modules are inspected
- **THEN** there is no `CookiesSettings` class
