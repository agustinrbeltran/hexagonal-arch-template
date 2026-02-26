## REMOVED Requirements

### Requirement: RefreshToken dataclass at account/infrastructure/security/refresh_token.py
**Reason**: Supabase GoTrue manages refresh tokens in `auth.refresh_tokens` and `auth.sessions`. The backend no longer stores or manages refresh tokens directly.
**Migration**: Remove `RefreshToken` dataclass. The `TokenPairRefresher` port implementation calls Supabase's refresh endpoint instead of querying a local table.

### Requirement: RefreshTokenRepository protocol at account/infrastructure/security/refresh_token_repository.py
**Reason**: No local refresh token storage. Supabase manages refresh token persistence.
**Migration**: Remove `RefreshTokenRepository` protocol and its SQLAlchemy implementation (`SqlaRefreshTokenRepository`).

### Requirement: RefreshTokenService at account/infrastructure/security/refresh_token_service.py
**Reason**: Token pair issuance, refresh, and revocation are handled by the Supabase client adapter(s) implementing `TokenPairIssuer`, `TokenPairRefresher`, and `AccessRevoker`.
**Migration**: Remove `RefreshTokenService`. Replace with Supabase adapter implementations for the respective ports.

### Requirement: Refresh token table references accounts
**Reason**: The `public.refresh_tokens` table is dropped. Supabase manages refresh tokens in `auth.refresh_tokens`.
**Migration**: Drop `public.refresh_tokens` table. Remove the SQLAlchemy table definition and mapper.
