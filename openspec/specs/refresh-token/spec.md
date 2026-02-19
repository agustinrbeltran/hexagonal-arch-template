## MODIFIED Requirements

### Requirement: RefreshToken dataclass at account/infrastructure/security/refresh_token.py
The system SHALL define a `RefreshToken` dataclass in `account/infrastructure/security/refresh_token.py` with fields: `id_` (str, opaque token ID), `account_id` (AccountId, from shared kernel), `expiration` (datetime). The `user_id` field SHALL be renamed to `account_id`.

#### Scenario: RefreshToken contains ID, account_id, and expiration
- **WHEN** a RefreshToken instance is created
- **THEN** it has `id_` (str), `account_id` (AccountId), and `expiration` (datetime) fields

#### Scenario: RefreshToken ID is cryptographically random
- **WHEN** a refresh token is issued
- **THEN** its `id_` is generated using `secrets.token_urlsafe(32)`

#### Scenario: RefreshToken is a plain dataclass
- **WHEN** inspecting `RefreshToken` in `account/infrastructure/security/refresh_token.py`
- **THEN** it is a `@dataclass` with no DDD base class

### Requirement: RefreshTokenRepository protocol at account/infrastructure/security/refresh_token_repository.py
The system SHALL define a `RefreshTokenRepository` protocol in `account/infrastructure/security/refresh_token_repository.py` with methods: `add(token)`, `get_by_id(token_id)`, `delete(token_id)`, `delete_all_for_account(account_id)`. The `delete_all_for_user` method SHALL be renamed to `delete_all_for_account`.

#### Scenario: RefreshTokenRepository has account-based method
- **WHEN** an infrastructure adapter implements `RefreshTokenRepository`
- **THEN** it has a `delete_all_for_account(account_id)` method

### Requirement: RefreshTokenService at account/infrastructure/security/refresh_token_service.py
The system SHALL define `RefreshTokenService` in `account/infrastructure/security/refresh_token_service.py`. It SHALL implement both `TokenPairIssuer` and `TokenPairRefresher` application-layer ports. All `user_id` parameters and fields SHALL be renamed to `account_id` using `AccountId` from shared kernel.

#### Scenario: RefreshTokenService implements TokenPairIssuer
- **WHEN** inspecting `RefreshTokenService`
- **THEN** it has an `issue_token_pair(account_id: AccountId) -> tuple[str, str]` method

#### Scenario: issue_token_pair creates both tokens
- **WHEN** `issue_token_pair(account_id)` is called
- **THEN** it creates a RefreshToken in the DB, generates a JWT access token, and returns both

#### Scenario: revoke_all_for_account deletes all tokens
- **WHEN** `revoke_all_for_account(account_id)` is called
- **THEN** all refresh tokens for that account are deleted from storage

### Requirement: Refresh token table references accounts
The `refresh_tokens` table column `user_id` SHALL be renamed to `account_id` and reference the `accounts` table instead of `users`.

#### Scenario: Refresh token mapper uses account_id
- **WHEN** the SQLAlchemy mapper for `refresh_tokens` is inspected
- **THEN** it maps `account_id` (UUID FK to accounts.id)
