## Why

The README.md is significantly outdated after the cookie-to-JWT authentication transition. It still describes an `AuthSession` domain aggregate, cookie-based sessions, a `/logout` endpoint, and session-based authentication flows — none of which exist anymore. This misleads anyone reading the documentation and needs to be brought in line with the current JWT + refresh token architecture.

## What Changes

- Remove all references to the `AuthSession` domain aggregate (entity, events, services, gateway) — it no longer exists
- Replace cookie-based session authentication descriptions with JWT access token + refresh token architecture
- Update API endpoint documentation: remove `/logout`, add `/refresh`
- Update the project structure tree to reflect current file layout (new security files, removed auth_session domain, new application use cases)
- Update request flow examples to show JWT-based authentication instead of session-based
- Update aggregate boundary diagrams — only `User` aggregate remains in the domain
- Add JWT configuration details (`JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRY_MIN`, `REFRESH_TOKEN_EXPIRY_DAYS`)
- Update code examples in architecture sections to match current implementation
- Update the login handler example to reflect token pair issuance instead of session creation

## Capabilities

### New Capabilities

_None — this is a documentation-only change._

### Modified Capabilities

_None — no spec-level behavior changes; this updates documentation to match already-implemented behavior._

## Impact

- **Files**: `README.md` (single file, extensive edits across multiple sections)
- **No code changes**: purely documentation
- **No API changes**: documenting what already exists
- **No dependency changes**: tech stack section is still accurate
