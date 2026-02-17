## Why

The current authentication uses server-side sessions stored in the database with JWT tokens delivered via HTTP-only cookies. This couples the API to browser-based clients and requires a database round-trip on every authenticated request to validate/extend the session. Replacing this with stateless JWT access tokens (returned in the response body, sent via `Authorization: Bearer` header) plus server-side refresh tokens makes the API client-agnostic, eliminates per-request session lookups, and follows the standard OAuth 2.0 bearer token pattern.

## What Changes

- **BREAKING**: Login endpoint returns `200 + JSON body` with `access_token` and `refresh_token` instead of `204 + Set-Cookie`
- **BREAKING**: Authenticated requests must send `Authorization: Bearer <token>` header instead of relying on cookies
- **BREAKING**: Logout endpoint (`DELETE /api/v1/account/logout`) is removed — clients discard tokens locally
- New `POST /api/v1/account/refresh` endpoint to exchange a valid refresh token for a new access + refresh token pair (rotation)
- JWT payload changes from `{auth_session_id, exp}` to `{sub: user_id, exp, iat}` (RFC 7519 standard claims)
- Access tokens are short-lived (15 min), stateless (no DB lookup on each request)
- Refresh tokens are long-lived (7 days), opaque strings stored server-side, rotated on use
- Cookie-handling ASGI middleware is removed entirely
- `auth_sessions` DB table is repurposed as `refresh_tokens`
- `AccessRevoker` implementation changes to delete refresh tokens (access tokens expire naturally)
- The "already authenticated" check on login is removed — clients simply get a new token pair

## Capabilities

### New Capabilities
- `jwt-bearer-auth`: Stateless JWT access token authentication via Authorization header, with refresh token rotation for session continuity
- `refresh-token`: Server-side refresh token issuance, validation, rotation, and revocation

### Modified Capabilities
- `auth-session-aggregate`: Replaced by refresh token entity — session concept removed, refresh token stored in DB instead
- `application-use-cases`: `log_out` use case removed, `log_in` returns token pair, new `refresh_token` use case added
- `infrastructure-adapters`: Cookie transport/middleware removed, Bearer token identity provider added, refresh token persistence adapter replaces session gateway

## Impact

- **API contract**: Login response schema changes (breaking), logout endpoint removed (breaking), all authenticated endpoints now require Bearer header (breaking)
- **Database**: `auth_sessions` table renamed/replaced with `refresh_tokens` (migration required)
- **Infrastructure layer**: ~12 files deleted (cookie middleware, session transport, logout controller), ~10 files modified (DI, settings, login handler/controller, identity provider), ~3 new files (refresh endpoint, token response model, bearer identity provider)
- **Domain layer**: `domain/auth_session/` heavily refactored — entity becomes `RefreshToken`, service simplified, gateway becomes repository
- **Config**: `SESSION_TTL_MIN`, `SESSION_REFRESH_THRESHOLD`, and `[security.cookies]` settings removed; `ACCESS_TOKEN_EXPIRY_MIN` and `REFRESH_TOKEN_EXPIRY_DAYS` added
- **Client impact**: All API consumers must update to send Bearer tokens and handle token refresh
