## Context

The application currently authenticates users via server-side sessions: on login, an `AuthSession` record is persisted to the `auth_sessions` DB table, a JWT containing the session ID is set as an HTTP-only cookie, and every authenticated request decodes the cookie, looks up the session in the database, validates expiry, and optionally extends the session's TTL. Logout deletes the session record and clears the cookie.

This approach tightly couples the API to browser clients (cookies), adds a DB round-trip per authenticated request, and requires server-side session management infrastructure (gateway, transport, timer, ID generator, ASGI middleware).

The target is a stateless JWT bearer token model with refresh token rotation, following standard OAuth 2.0 patterns.

## Goals / Non-Goals

**Goals:**
- Replace cookie-based session auth with `Authorization: Bearer <token>` header authentication
- Return access + refresh tokens as JSON from the login endpoint
- Stateless access token validation (no DB lookup per request)
- Server-side refresh token storage with rotation on use
- Maintain the `is_active` check on every request via `CurrentUserHandler`
- Preserve `AccessRevoker` capability by deleting refresh tokens on user deactivation
- Remove all cookie/session infrastructure

**Non-Goals:**
- OAuth 2.0 authorization server (no scopes, no third-party client grants)
- Token denylist / blacklist for access tokens
- Embedding user role in the JWT payload (role checked from DB via `CurrentUserHandler`)
- Refresh token device/client tracking (no device fingerprinting)
- Rate limiting on the refresh endpoint

## Decisions

### 1. JWT payload: standard claims only

**Decision**: Use `{sub: str(user_id), exp: int, iat: int}` — nothing else.

**Rationale**: Keeping the token minimal avoids stale-data problems (e.g., role in token doesn't match DB). Since `CurrentUserHandler` already loads the user from the DB on every request, there's no benefit to duplicating data in the token.

**Alternative considered**: Include `role` claim to skip DB lookup for authorization. Rejected because role changes wouldn't take effect until token refresh, and the DB lookup is already happening.

### 2. Refresh token rotation

**Decision**: On each `POST /refresh`, issue a new access token AND a new refresh token, invalidating the old refresh token.

**Rationale**: Rotation limits the window for stolen refresh tokens. If a token is compromised and used by an attacker, the legitimate user's next refresh attempt fails (token already consumed), signaling compromise. This is the standard recommendation for public clients.

**Alternative considered**: Reuse the same refresh token until it expires. Simpler, but a stolen token grants access for the full refresh token lifetime (7 days) with no detection mechanism.

### 3. Repurpose `auth_sessions` table as `refresh_tokens`

**Decision**: Rename and reuse the existing table structure rather than drop + recreate.

**Rationale**: The schema is nearly identical (`id`, `user_id`, `expiration`). A rename migration is simpler and preserves the foreign key relationship. The gateway/mapper code transforms with minimal structural change.

**Alternative considered**: Drop `auth_sessions`, create `refresh_tokens` from scratch. Cleaner conceptually but more migration work for identical outcome.

### 4. Collapse `AuthSessionService` into `RefreshTokenService`

**Decision**: Replace `AuthSessionService` (issue, validate, extend, terminate) with `RefreshTokenService` providing: `issue_token_pair(user_id)`, `refresh(refresh_token_id)`, `revoke_all_for_user(user_id)`.

**Rationale**: The new service is simpler — no session extension logic, no cookie transport, no cached session state. The refresh flow is: look up token → validate expiry → delete old token → create new pair.

### 5. `IdentityProvider` reads from `Authorization` header directly

**Decision**: The new `JwtBearerIdentityProvider` extracts the token from `Authorization: Bearer <token>`, decodes it with `JwtAccessTokenProcessor`, and returns the `user_id`. No DB call, no session service dependency.

**Rationale**: This is the core simplification — identity extraction becomes stateless. The `CurrentUserHandler` still does the DB call to verify `is_active`, but the identity provider itself is pure JWT decode.

### 6. Login returns `200 + JSON` instead of `204 + Set-Cookie`

**Decision**: Response model: `{"access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 900}`.

**Rationale**: Standard OAuth 2.0 token response format. `expires_in` is in seconds (15 min = 900s). Clients use this to know when to refresh.

### 7. Remove `AlreadyAuthenticatedError` check from login

**Decision**: Drop the check entirely. Any valid credentials produce a new token pair.

**Rationale**: With stateless tokens, the concept of "already authenticated" is meaningless — there's no server-side session to conflict with. Multiple concurrent tokens for the same user are fine.

### 8. `AccessRevoker` deletes refresh tokens

**Decision**: `RefreshTokenAccessRevoker.remove_all_user_access(user_id)` deletes all refresh tokens for the user. Existing access tokens expire naturally (max 15 min).

**Rationale**: This maintains the existing contract used by `CurrentUserHandler` and `DeactivateUserHandler`. The 15-minute window is acceptable because `CurrentUserHandler` already checks `is_active` on every request — a deactivated user is blocked immediately regardless of token validity.

### 9. OpenAPI security scheme: `HTTPBearer`

**Decision**: Replace `APIKeyCookie(name="access_token")` with `HTTPBearer()` from `fastapi.security`.

**Rationale**: Standard OpenAPI 3.0 bearer auth scheme. Swagger UI will show an "Authorize" button that accepts a Bearer token.

### 10. Token expiry configuration

**Decision**:
- Access token: `ACCESS_TOKEN_EXPIRY_MIN = 15` (configurable)
- Refresh token: `REFRESH_TOKEN_EXPIRY_DAYS = 7` (configurable)
- Remove: `SESSION_TTL_MIN`, `SESSION_REFRESH_THRESHOLD`, `[security.cookies]`

## Risks / Trade-offs

**[Risk] Access tokens can't be instantly revoked** → Mitigated by short expiry (15 min) and `CurrentUserHandler` checking `is_active` on every request. A deactivated user is blocked on next API call regardless.

**[Risk] Refresh token rotation adds complexity** → Mitigated by keeping the implementation simple: delete old + create new in a single transaction. No replay detection or token families.

**[Risk] Breaking API changes affect all clients** → Mitigated by this being a template project, not a production system with existing consumers. No backward compatibility needed.

**[Trade-off] DB lookup still happens per request** → `CurrentUserHandler` fetches the user to check `is_active`. This is intentional — it's the safety net for deactivated users. The session table lookup is what's eliminated.

## Migration Plan

1. Create DB migration: rename `auth_sessions` → `refresh_tokens` (schema unchanged)
2. Deploy code changes (all in one release — no gradual rollout needed for a template)
3. Rollback: revert code + reverse migration

## Open Questions

None — all decisions resolved during exploration.
