## Context

The backend uses a custom auth stack: `public.accounts` stores credentials (bcrypt + HMAC pepper), `public.refresh_tokens` stores opaque refresh tokens, and PyJWT handles access token creation/verification. The `AccountService` domain service orchestrates ID generation and password hashing. The `LogInHandler` verifies passwords locally and issues tokens via `TokenPairIssuer`.

Supabase's GoTrue service already runs alongside the backend on the same Postgres instance. It manages `auth.users`, `auth.sessions`, and `auth.refresh_tokens`. The goal is to delegate all credential management to GoTrue while keeping domain-specific authorization (roles, is_active, permissions) in the backend.

The hexagonal architecture demands that Supabase never appears in the Domain or Application layers. All Supabase interactions happen behind application-layer Protocols, wired via DI.

## Goals / Non-Goals

**Goals:**
- Delegate credential storage, password hashing, and session management to Supabase GoTrue
- Introduce application-layer ports (`AccountProvisioner`, `PasswordResetter`) for credential operations
- Change `TokenPairIssuer` to accept credentials and return tokens (Supabase handles auth + token issuance as one operation)
- Replace `public.accounts` with `public.account_metadata` (role + is_active only)
- Verify Supabase-issued JWTs in the existing `JwtBearerIdentityProvider` using the shared JWT secret
- Keep the API contract unchanged (same endpoints, same request/response shapes)

**Non-Goals:**
- Client-side direct Supabase auth (all auth flows still go through the backend)
- Social login, MFA, or email verification (future work enabled by this migration)
- Migrating existing user passwords (HMAC pepper makes this impossible; users must reset)
- Changing the permission framework or role system
- RLS policies on `account_metadata` (can be added later)

## Decisions

### 1. Account metadata in a separate `public.account_metadata` table

Store only `account_id` (PK, FK to `auth.users.id`), `role`, and `is_active` in `public.account_metadata`. Email is read-only from `auth.users`.

**Why not `raw_app_meta_data` on `auth.users`?** JSONB queries are awkward, no typed enum in the DB, and it couples the domain to Supabase's schema conventions.

**Why not keep `public.accounts` with email duplicated?** Duplication risks drift. Option B (metadata-only) is cleaner and accepts that email is owned by the auth provider.

**Implication**: `AccountRepository` reads require a cross-schema join (`auth.users JOIN public.account_metadata`). Writes only touch `account_metadata`. The `Account` entity never exposes a `change_email()` method.

### 2. `AccountProvisioner` as a new application-layer port

```python
class AccountProvisioner(Protocol):
    async def register(self, email: Email, password: RawPassword) -> AccountId: ...
```

The `SignUpHandler` calls this port to register credentials, receives the Supabase-generated UUID, then creates the `Account` aggregate (with role/is_active) and saves metadata.

**Why a new port instead of extending `AccountRepository`?** The repository persists aggregates — it shouldn't accept raw passwords. Credential registration is a fundamentally different responsibility.

**Why not extend `TokenPairIssuer`?** Registration and authentication are distinct operations with different return types.

### 3. `TokenPairIssuer` signature change to `(email, password)`

```python
class TokenPairIssuer(Protocol):
    @property
    def access_token_expiry_seconds(self) -> int: ...

    async def issue_token_pair(self, email: Email, password: RawPassword) -> tuple[str, str]: ...
```

The Supabase adapter calls `sign_in_with_password(email, password)` which verifies credentials and returns tokens in one operation. The `LogInHandler` no longer verifies passwords — it delegates entirely to this port.

**`access_token_expiry_seconds`**: The adapter reads this from configuration (mirroring the Supabase JWT expiry setting) or computes it from the returned token's `exp` claim.

**Note**: The method becomes `async` since the Supabase call is a network operation.

### 4. `PasswordResetter` as a new application-layer port

```python
class PasswordResetter(Protocol):
    async def reset_password(self, account_id: AccountId, new_password: RawPassword) -> None: ...
```

Infrastructure adapter uses the Supabase admin API (`admin.update_user_by_id()`). The `ChangePasswordHandler` delegates to this port instead of `AccountService.change_password()`.

### 5. `TokenPairRefresher` and `AccessRevoker` stay as ports, implementations change

`TokenPairRefresher.refresh()` — Supabase adapter calls GoTrue's refresh endpoint.
`AccessRevoker.remove_all_account_access()` — Supabase adapter calls admin API to revoke sessions.

The port signatures may need minor adjustments (e.g., `refresh` may need to accept/return different token formats if Supabase's refresh token structure differs from the current opaque string).

### 6. JWT verification with shared secret and audience validation

The `JwtAccessTokenProcessor` adds `audience="authenticated"` to `jwt.decode()`. The `jwt_secret` config value now points to the Supabase JWT secret. The `sub` claim format is the same (UUID string), so `JwtBearerIdentityProvider` works with minimal changes.

**Encoding is removed** — the backend no longer issues its own JWTs. `JwtAccessTokenProcessor` becomes verify-only (`AccessTokenDecoder`).

### 7. Remove `AccountService`, `PasswordHasher`, `BcryptPasswordHasher`, `AccountIdGenerator`

`AccountService` loses all responsibilities:
- ID generation → Supabase generates IDs via `AccountProvisioner`
- Password hashing → Supabase handles via `AccountProvisioner` / `TokenPairIssuer`
- Password verification → Supabase handles via `TokenPairIssuer`
- Password changing → Supabase handles via `PasswordResetter`

The `Account.create()` classmethod is called directly by handlers with the ID returned from `AccountProvisioner`. No domain service needed.

### 8. `profiles.account_id` FK references `auth.users.id` directly

No intermediate table. The profile's foreign key points straight to Supabase's `auth.users.id`.

### 9. Remove `AuthUnitOfWork`, `RefreshToken`, `RefreshTokenRepository`, `RefreshTokenService`

Supabase manages sessions and refresh tokens entirely. The `auth_unit_of_work.commit()` call in `LogInHandler` is removed. The `public.refresh_tokens` table is dropped.

### 10. Supabase client as an infrastructure dependency

A single Supabase client instance (using `supabase-py`) is created at the DI level (`Scope.APP`) and injected into adapters. Configuration: `supabase_url` and `supabase_service_role_key` added to settings.

The service role key is required for admin operations (create user, update user, revoke sessions). Standard client operations use the anon key.

## Risks / Trade-offs

**[Password migration impossible]** → Existing users must reset their passwords after migration. The HMAC pepper means current hashes can't be verified by GoTrue. Mitigation: since there's only 1 row in `public.accounts`, this is a non-issue for now.

**[Cross-schema join performance]** → `auth.users JOIN account_metadata` on every account lookup. Mitigation: both tables are small, the join is on a UUID PK/FK. Acceptable.

**[Email drift]** → If email is changed directly in Supabase dashboard, the backend won't know. Mitigation: the backend doesn't store email — it always reads from `auth.users`. No drift possible by design.

**[Supabase coupling in infrastructure]** → If Supabase is replaced, all adapters need rewriting. Mitigation: that's the entire point of hexagonal architecture — adapters are the replaceable part.

**[Network latency on auth operations]** → `sign_up()`, `sign_in_with_password()`, and `refresh()` are now network calls to GoTrue instead of local DB operations. Mitigation: GoTrue runs on the same host in local/dev environments. In production, latency is minimal (same cloud region).

**[`issue_token_pair` becomes async]** → Currently synchronous. Changing to async affects the port signature and all callers. Mitigation: the handler is already async, so this is a straightforward change.

## Migration Plan

1. Add `supabase-py` dependency
2. Create `public.account_metadata` table via migration
3. Migrate existing account data: insert metadata rows, create corresponding `auth.users` entries via admin API
4. Update `profiles.account_id` FK to reference `auth.users.id`
5. Drop `public.accounts` and `public.refresh_tokens` tables
6. Deploy new adapters, remove old infrastructure code
7. Rollback: re-create `public.accounts` from `auth.users` + `account_metadata`, restore old adapters

## Open Questions

- Should the Supabase adapter use the admin API (`admin.create_user`) or the client API (`sign_up`) for registration? Admin API bypasses email confirmation and allows setting `app_metadata`. Client API triggers the standard GoTrue flow.
- What happens when `TokenPairIssuer.issue_token_pair()` fails due to wrong credentials? The adapter should raise an `AuthenticationError` — but should this be a domain error or an infrastructure error that gets mapped?
- Should `RawPassword` validation (min 6 chars) remain in the domain layer as a value object, or is it redundant since Supabase enforces its own password policy?
