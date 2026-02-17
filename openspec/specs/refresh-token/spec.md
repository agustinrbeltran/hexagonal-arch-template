## ADDED Requirements

### Requirement: RefreshToken dataclass at infrastructure/security/refresh_token.py
The system SHALL define a `RefreshToken` dataclass in `infrastructure/security/refresh_token.py` with fields: `id_` (str, opaque token ID), `user_id` (UserId), `expiration` (datetime). The refresh token is an opaque server-side credential — it is NOT a JWT. This is an infrastructure-internal data structure, NOT a domain entity or aggregate root.

#### Scenario: RefreshToken contains ID, user_id, and expiration
- **WHEN** a RefreshToken instance is created
- **THEN** it has `id_` (str), `user_id` (UserId), and `expiration` (datetime) fields

#### Scenario: RefreshToken ID is cryptographically random
- **WHEN** a refresh token is issued
- **THEN** its `id_` is generated using `secrets.token_urlsafe(32)`

#### Scenario: RefreshToken is a plain dataclass
- **WHEN** inspecting `RefreshToken` in `infrastructure/security/refresh_token.py`
- **THEN** it is a `@dataclass` with no DDD base class (not Entity, not AggregateRoot, not ValueObject)

#### Scenario: RefreshToken is not importable from domain layer
- **WHEN** searching for `RefreshToken` imports across `src/domain/`
- **THEN** no domain module imports `RefreshToken`

### Requirement: RefreshTokenRepository protocol at infrastructure/security/refresh_token_repository.py
The system SHALL define a `RefreshTokenRepository` protocol in `infrastructure/security/refresh_token_repository.py` with methods: `add(token)`, `get_by_id(token_id)`, `delete(token_id)`, `delete_all_for_user(user_id)`. This is an infrastructure-internal contract implemented by the SQLAlchemy adapter.

#### Scenario: RefreshTokenRepository is a protocol-based port
- **WHEN** an infrastructure adapter implements `RefreshTokenRepository`
- **THEN** it satisfies the protocol via structural typing

#### Scenario: RefreshTokenRepository is an infrastructure-internal protocol
- **WHEN** inspecting imports of `RefreshTokenRepository`
- **THEN** it is imported only by infrastructure modules (persistence adapter, security service), never by domain or application layers

### Requirement: RefreshToken errors at infrastructure/security/errors.py
The system SHALL define `RefreshTokenNotFoundError` and `RefreshTokenExpiredError` in `infrastructure/security/errors.py`. These errors SHALL NOT extend `DomainError` — they are infrastructure-level auth errors.

#### Scenario: RefreshTokenNotFoundError is raised for missing tokens
- **WHEN** a refresh token ID does not exist in storage
- **THEN** `RefreshTokenNotFoundError` is raised

#### Scenario: RefreshTokenExpiredError is raised for expired tokens
- **WHEN** a refresh token exists but its expiration is in the past
- **THEN** `RefreshTokenExpiredError` is raised

#### Scenario: RefreshTokenNotFoundError is not a DomainError
- **WHEN** inspecting `RefreshTokenNotFoundError` in `infrastructure/security/errors.py`
- **THEN** it does NOT inherit from `DomainError`

#### Scenario: HTTP error handler still maps token errors to 401
- **WHEN** a `RefreshTokenNotFoundError` or `RefreshTokenExpiredError` is raised during request handling
- **THEN** it is mapped to HTTP 401 Unauthorized

### Requirement: RefreshTokenService at infrastructure/security/refresh_token_service.py
The system SHALL define `RefreshTokenService` in `infrastructure/security/refresh_token_service.py`. It SHALL implement both `TokenPairIssuer` and `TokenPairRefresher` application-layer ports. It contains the token lifecycle logic: creation, rotation, expiry checking, and revocation. It also exposes `revoke_all_for_user(user_id)` for access revocation.

#### Scenario: RefreshTokenService implements TokenPairIssuer
- **WHEN** inspecting `RefreshTokenService`
- **THEN** it has an `issue_token_pair(user_id: UserId) -> tuple[str, str]` method compatible with the `TokenPairIssuer` protocol

#### Scenario: RefreshTokenService implements TokenPairRefresher
- **WHEN** inspecting `RefreshTokenService`
- **THEN** it has a `refresh(refresh_token_id: str) -> tuple[str, str]` method compatible with the `TokenPairRefresher` protocol

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
