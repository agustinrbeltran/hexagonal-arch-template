## Why

The backend currently manages the entire authentication lifecycle (password hashing, JWT issuance, refresh token storage) using custom infrastructure (`public.accounts`, bcrypt with HMAC pepper, PyJWT, opaque refresh tokens). Supabase already provides a battle-tested auth system via GoTrue (`auth.users`, `auth.sessions`, `auth.refresh_tokens`). Migrating to Supabase Auth eliminates redundant credential management, unlocks future features (email verification, social login, password reset flows), and lets the backend focus on domain-specific authorization logic.

## What Changes

- **BREAKING**: Remove `password_hash` from the `Account` aggregate. Credentials are now managed entirely by the external auth provider (Supabase GoTrue).
- **BREAKING**: Remove `AccountService` domain service. Its responsibilities (ID generation, password hashing, password verification) move behind application-layer ports.
- **BREAKING**: Remove `AccountPasswordHash` value object, `PasswordHasher` domain port, and `BcryptPasswordHasher` infrastructure adapter.
- **BREAKING**: Replace `public.accounts` table with `public.account_metadata` (account_id FK to `auth.users.id`, role, is_active). The `Account` aggregate's email becomes read-only, sourced from `auth.users` via cross-schema join.
- **BREAKING**: Remove `public.refresh_tokens` table. Supabase manages sessions and refresh tokens in `auth.sessions` / `auth.refresh_tokens`.
- **BREAKING**: Change `TokenPairIssuer.issue_token_pair()` signature from `(account_id: AccountId)` to `(email: Email, password: RawPassword)`. The port now encompasses both credential verification and token issuance.
- Add new `AccountProvisioner` application-layer port: `register(email, password) -> AccountId`. Infrastructure adapter calls Supabase `sign_up()`.
- Add new `PasswordResetter` application-layer port for delegated password changes. Infrastructure adapter calls Supabase admin API.
- `TokenPairRefresher` and `AccessRevoker` ports remain; implementations change to use Supabase client.
- Remove `AuthUnitOfWork` (Supabase manages session persistence).
- Update `JwtBearerIdentityProvider` to validate Supabase JWTs (shared JWT secret, `audience="authenticated"`).
- Update `profiles.account_id` FK to reference `auth.users.id` directly instead of `public.accounts.id`.

## Capabilities

### New Capabilities
- `auth-provider-ports`: Application-layer ports (`AccountProvisioner`, `PasswordResetter`) that abstract credential management away from the domain. Infrastructure adapters implement these using the Supabase client.

### Modified Capabilities
- `account-aggregate`: Remove `password_hash` field, `AccountPasswordHash` value object, `change_password()` method, `AccountPasswordChanged` event, `AccountService`, `PasswordHasher` port, and `AccountIdGenerator` port.
- `token-management-ports`: Change `TokenPairIssuer.issue_token_pair()` signature to `(email: Email, password: RawPassword)`. Remove `AuthUnitOfWork`.
- `refresh-token`: Remove custom `RefreshToken` dataclass, `RefreshTokenRepository`, `RefreshTokenService`, `RefreshTokenIdGenerator`, and `public.refresh_tokens` table. Supabase manages refresh tokens.
- `jwt-bearer-auth`: Add `audience="authenticated"` validation. JWT secret is now the Supabase JWT secret (shared via config).
- `infrastructure-adapters`: Remove `BcryptPasswordHasher`, `SqlaAuthUnitOfWork`, `SqlaRefreshTokenRepository`. Replace `SqlaAccountRepository` to read from `auth.users JOIN account_metadata` and write to `account_metadata` only. Add Supabase adapter(s). Update DI providers. Database migration replaces `public.accounts` with `public.account_metadata` and drops `public.refresh_tokens`. Update `profiles.account_id` FK to `auth.users.id`.

## Impact

- **Database**: New migration to create `account_metadata`, drop `accounts` and `refresh_tokens`, update `profiles` FK. Existing account data requires migration to `auth.users` (password cannot be ported due to HMAC pepper — user must reset password).
- **Dependencies**: Add `supabase-py` (or `gotrue-py`) as a new dependency.
- **Configuration**: New settings for Supabase URL and service role key. Existing `jwt_secret` points to Supabase JWT secret. Password-related settings (`pepper`, `hasher_work_factor`, etc.) are removed.
- **Tests**: All unit tests touching `AccountService`, `PasswordHasher`, `BcryptPasswordHasher`, `RefreshTokenService`, and the login/signup handlers will need updates. Tests for new Supabase adapters needed.
- **API contract**: Login/signup HTTP endpoints stay the same (email + password in, tokens/id out). No client-facing breaking changes.
