## ADDED Requirements

### Requirement: RefreshToken entity at domain/refresh_token/entity.py
The system SHALL define a `RefreshToken` dataclass in `domain/refresh_token/entity.py` with fields: `id_` (str, opaque token ID), `user_id` (UserId), `expiration` (datetime). The refresh token is an opaque server-side credential — it is NOT a JWT.

#### Scenario: RefreshToken contains ID, user_id, and expiration
- **WHEN** a RefreshToken instance is created
- **THEN** it has `id_` (str), `user_id` (UserId), and `expiration` (datetime) fields

#### Scenario: RefreshToken ID is cryptographically random
- **WHEN** a refresh token is issued
- **THEN** its `id_` is generated using `secrets.token_urlsafe(32)`

### Requirement: RefreshToken repository port at domain/refresh_token/repository.py
The system SHALL define a `RefreshTokenRepository` protocol in `domain/refresh_token/repository.py` with methods: `add(token)`, `get_by_id(token_id)`, `delete(token_id)`, `delete_all_for_user(user_id)`.

#### Scenario: RefreshTokenRepository is a protocol-based port
- **WHEN** an infrastructure adapter implements `RefreshTokenRepository`
- **THEN** it satisfies the protocol via structural typing

### Requirement: RefreshToken domain errors at domain/refresh_token/errors.py
The system SHALL define `RefreshTokenNotFoundError` and `RefreshTokenExpiredError` in `domain/refresh_token/errors.py`.

#### Scenario: RefreshTokenNotFoundError is raised for missing tokens
- **WHEN** a refresh token ID does not exist in storage
- **THEN** `RefreshTokenNotFoundError` is raised

#### Scenario: RefreshTokenExpiredError is raised for expired tokens
- **WHEN** a refresh token exists but its expiration is in the past
- **THEN** `RefreshTokenExpiredError` is raised

### Requirement: RefreshTokenService at domain/refresh_token/services.py
The system SHALL define a `RefreshTokenService` with methods: `issue_token_pair(user_id)` returning `(access_token_str, refresh_token_str)`, `refresh(refresh_token_id)` returning `(access_token_str, refresh_token_str)`, and `revoke_all_for_user(user_id)`.

#### Scenario: issue_token_pair creates both tokens
- **WHEN** `issue_token_pair(user_id)` is called
- **THEN** it creates a RefreshToken in the DB, generates a JWT access token, and returns both

#### Scenario: refresh rotates the refresh token
- **WHEN** `refresh(old_token_id)` is called with a valid refresh token
- **THEN** the old refresh token is deleted, a new refresh token is created, and a new access token is generated

#### Scenario: refresh rejects expired refresh token
- **WHEN** `refresh(token_id)` is called with an expired refresh token
- **THEN** `RefreshTokenExpiredError` is raised

#### Scenario: refresh rejects unknown refresh token
- **WHEN** `refresh(token_id)` is called with a non-existent token ID
- **THEN** `RefreshTokenNotFoundError` is raised

#### Scenario: revoke_all_for_user deletes all tokens
- **WHEN** `revoke_all_for_user(user_id)` is called
- **THEN** all refresh tokens for that user are deleted from storage

### Requirement: Refresh endpoint at POST /api/v1/account/refresh
The system SHALL provide a `POST /api/v1/account/refresh` endpoint that accepts a JSON body with `refresh_token` (string). On success, it MUST return `200 OK` with a new token pair (same schema as login response). On invalid/expired token, it MUST return `401 Unauthorized`.

#### Scenario: Valid refresh token returns new token pair
- **WHEN** `POST /api/v1/account/refresh` is called with a valid refresh token
- **THEN** response is `200 OK` with `access_token`, `refresh_token`, `token_type`, and `expires_in`

#### Scenario: Invalid refresh token returns 401
- **WHEN** `POST /api/v1/account/refresh` is called with an invalid or expired refresh token
- **THEN** response is `401 Unauthorized`

### Requirement: Refresh token expiry is configurable
The system SHALL read `REFRESH_TOKEN_EXPIRY_DAYS` from configuration (default: 7). The refresh token's `expiration` MUST be set to `now + REFRESH_TOKEN_EXPIRY_DAYS` at creation time.

#### Scenario: Refresh token expiry uses configured value
- **WHEN** a refresh token is created with `REFRESH_TOKEN_EXPIRY_DAYS = 7`
- **THEN** its expiration is 7 days from creation time
