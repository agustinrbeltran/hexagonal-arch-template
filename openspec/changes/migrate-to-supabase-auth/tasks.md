## 1. Domain Layer Cleanup

- [ ] 1.1 Remove `password_hash` field from `Account` entity, remove `change_password()` method, remove `AccountPasswordChanged` event from `account/domain/account/events.py`
- [ ] 1.2 Remove `AccountPasswordHash` value object from `account/domain/account/value_objects.py`
- [ ] 1.3 Remove `PasswordHasher` and `AccountIdGenerator` ports from `account/domain/account/ports.py` (keep `AccessRevoker`)
- [ ] 1.4 Remove `AccountService` class from `account/domain/account/services.py` (keep permission classes: `CanManageSelf`, `CanManageSubordinate`, `CanManageRole`)
- [ ] 1.5 Update `Account.create()` signature to no longer require `password_hash`

## 2. Application Layer Ports

- [ ] 2.1 Create `AccountProvisioner` protocol in `account/application/shared/account_provisioner.py` with `register(email: Email, password: RawPassword) -> AccountId`
- [ ] 2.2 Create `PasswordResetter` protocol in `account/application/shared/password_resetter.py` with `reset_password(account_id: AccountId, new_password: RawPassword) -> None`
- [ ] 2.3 Change `TokenPairIssuer` signature in `account/application/shared/token_pair_issuer.py` to `async issue_token_pair(email: Email, password: RawPassword) -> tuple[str, str]`
- [ ] 2.4 Remove `AuthUnitOfWork` from `account/application/shared/auth_unit_of_work.py`

## 3. Application Layer Handlers

- [ ] 3.1 Update `SignUpHandler` to use `AccountProvisioner.register()` instead of `AccountService.create()`, call `Account.create()` directly with returned ID
- [ ] 3.2 Update `LogInHandler` to remove `AccountService` dependency and `is_password_valid` check, remove `AuthUnitOfWork` dependency, call `token_pair_issuer.issue_token_pair(email, password)`
- [ ] 3.3 Update `ChangePasswordHandler` to use `PasswordResetter.reset_password()` instead of `AccountService.change_password()`
- [ ] 3.4 Update any other handlers that depend on `AccountService` (check `CurrentAccountHandler`, admin use cases)

## 4. Database Migration

- [ ] 4.1 Create migration: create `public.account_metadata` table (`account_id` UUID PK FK to `auth.users(id)`, `role` accountrole NOT NULL DEFAULT 'USER', `is_active` BOOLEAN NOT NULL DEFAULT TRUE)
- [ ] 4.2 Create migration: update `profiles.account_id` FK to reference `auth.users(id)` instead of `accounts(id)`
- [ ] 4.3 Create migration: drop `public.refresh_tokens` table
- [ ] 4.4 Create migration: drop `public.accounts` table

## 5. Infrastructure — Persistence

- [ ] 5.1 Replace `AccountRecord` / accounts table mapper with `AccountMetadataRecord` / `account_metadata` table mapper in `account/infrastructure/persistence/mappers/account.py`. Add read-only `auth_users_table` reference (schema `"auth"`)
- [ ] 5.2 Update `AccountConverter` to convert between `Account` entity and the cross-schema join result (email from auth.users, role/is_active from account_metadata)
- [ ] 5.3 Update `SqlaAccountRepository` — `save()` writes to `account_metadata` only, `get_by_id()` / `get_by_email()` use cross-schema join, `get_all()` uses cross-schema join
- [ ] 5.4 Update `SqlaAccountUnitOfWork` — remove email-specific `IntegrityError` handling (email uniqueness is enforced by auth provider, not account_metadata)
- [ ] 5.5 Remove `SqlaAuthUnitOfWork`, `SqlaRefreshTokenRepository`, refresh token table mapper

## 6. Infrastructure — Supabase Adapters

- [ ] 6.1 Add `supabase-py` dependency
- [ ] 6.2 Add `SupabaseSettings` (url, service_role_key) to config settings, remove `PasswordSettings`
- [ ] 6.3 Create Supabase adapter implementing `AccountProvisioner` (uses `admin.create_user`)
- [ ] 6.4 Create Supabase adapter implementing `TokenPairIssuer` (uses `sign_in_with_password`)
- [ ] 6.5 Create Supabase adapter implementing `TokenPairRefresher` (uses refresh session endpoint)
- [ ] 6.6 Create Supabase adapter implementing `AccessRevoker` (uses admin API to revoke sessions)
- [ ] 6.7 Create Supabase adapter implementing `PasswordResetter` (uses `admin.update_user_by_id`)

## 7. Infrastructure — JWT & Identity

- [ ] 7.1 Update `JwtAccessTokenProcessor` — remove `encode()` method, add `audience="authenticated"` to `decode()`, rename to `AccessTokenDecoder` or similar
- [ ] 7.2 Update `JwtBearerIdentityProvider` if needed (should work with minimal changes since `sub` claim format is unchanged)

## 8. Infrastructure — DI Rewiring

- [ ] 8.1 Remove providers: `AccountService`, `PasswordHasher`, `AccountIdGenerator`, `HasherThreadPoolExecutor`, `HasherSemaphore`, `RefreshTokenService`, `RefreshTokenRepository`, `RefreshTokenIdGenerator`, `AuthUnitOfWork`, `AccessTokenEncoder`
- [ ] 8.2 Add providers: Supabase client (Scope.APP), `AccountProvisioner`, `PasswordResetter`
- [ ] 8.3 Update providers: `TokenPairIssuer`, `TokenPairRefresher`, `AccessRevoker` to use Supabase adapters
- [ ] 8.4 Update config: add Supabase settings to TOML config files, remove password hasher settings

## 9. Infrastructure — Cleanup

- [ ] 9.1 Remove `BcryptPasswordHasher` from `account/infrastructure/security/`
- [ ] 9.2 Remove `RefreshTokenService`, `RefreshToken` dataclass, `RefreshTokenIdGenerator`, `RefreshTokenRepository` from `account/infrastructure/security/`
- [ ] 9.3 Remove `UuidAccountIdGenerator` from `account/infrastructure/security/`
- [ ] 9.4 Clean up imports across the codebase (remove references to deleted modules)

## 10. Tests

- [ ] 10.1 Update unit tests for `Account` entity (remove password_hash from factories and assertions)
- [ ] 10.2 Update unit tests for `SignUpHandler` (mock `AccountProvisioner` instead of `AccountService`)
- [ ] 10.3 Update unit tests for `LogInHandler` (mock `TokenPairIssuer` with new signature, remove `AccountService` and `AuthUnitOfWork` mocks)
- [ ] 10.4 Update unit tests for `ChangePasswordHandler` (mock `PasswordResetter`)
- [ ] 10.5 Remove unit tests for `AccountService`, `BcryptPasswordHasher`, `RefreshTokenService`
- [ ] 10.6 Add unit tests for Supabase adapters (mock `supabase-py` client)
- [ ] 10.7 Run `make code.check` — ensure all linting and tests pass
