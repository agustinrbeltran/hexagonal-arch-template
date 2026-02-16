## ADDED Requirements

### Requirement: RefreshToken dataclass at infrastructure/security/refresh_token.py
The system SHALL define a `RefreshToken` dataclass in `infrastructure/security/refresh_token.py` with fields: `id_` (str), `user_id` (UserId), `expiration` (datetime). This is an infrastructure-internal data structure, NOT a domain entity or aggregate root.

#### Scenario: RefreshToken is a plain dataclass
- **WHEN** inspecting `RefreshToken` in `infrastructure/security/refresh_token.py`
- **THEN** it is a `@dataclass` with no DDD base class (not Entity, not AggregateRoot, not ValueObject)

#### Scenario: RefreshToken is not importable from domain layer
- **WHEN** searching for `RefreshToken` imports across `src/domain/`
- **THEN** no domain module imports `RefreshToken`

### Requirement: RefreshTokenRepository protocol at infrastructure/security/refresh_token_repository.py
The system SHALL define a `RefreshTokenRepository` protocol in `infrastructure/security/refresh_token_repository.py` with methods: `add(token)`, `get_by_id(token_id)`, `delete(token_id)`, `delete_all_for_user(user_id)`. This is an infrastructure-internal contract implemented by the SQLAlchemy adapter.

#### Scenario: RefreshTokenRepository is an infrastructure-internal protocol
- **WHEN** inspecting imports of `RefreshTokenRepository`
- **THEN** it is imported only by infrastructure modules (persistence adapter, security service), never by domain or application layers

### Requirement: RefreshTokenService at infrastructure/security/refresh_token_service.py
The system SHALL define `RefreshTokenService` in `infrastructure/security/refresh_token_service.py`. It SHALL implement both `TokenPairIssuer` and `TokenPairRefresher` application-layer ports. It contains the same logic as the previous `domain/refresh_token/services.py`: token creation, rotation, expiry checking, and revocation.

#### Scenario: RefreshTokenService implements TokenPairIssuer
- **WHEN** inspecting `RefreshTokenService`
- **THEN** it has an `issue_token_pair(user_id: UserId) -> tuple[str, str]` method compatible with the `TokenPairIssuer` protocol

#### Scenario: RefreshTokenService implements TokenPairRefresher
- **WHEN** inspecting `RefreshTokenService`
- **THEN** it has a `refresh(refresh_token_id: str) -> tuple[str, str]` method compatible with the `TokenPairRefresher` protocol

#### Scenario: RefreshTokenService preserves existing rotation logic
- **WHEN** `refresh(token_id)` is called with a valid, non-expired refresh token
- **THEN** the old token is deleted, a new refresh token is created, and a new access token is generated — identical behavior to before

### Requirement: Refresh token errors at infrastructure/security/errors.py
The system SHALL define `RefreshTokenNotFoundError` and `RefreshTokenExpiredError` in `infrastructure/security/errors.py`. These errors SHALL NOT extend `DomainError` — they are infrastructure-level auth errors.

#### Scenario: RefreshTokenNotFoundError is not a DomainError
- **WHEN** inspecting `RefreshTokenNotFoundError` in `infrastructure/security/errors.py`
- **THEN** it does NOT inherit from `DomainError`

#### Scenario: HTTP error handler still maps token errors to 401
- **WHEN** a `RefreshTokenNotFoundError` or `RefreshTokenExpiredError` is raised during request handling
- **THEN** it is mapped to HTTP 401 Unauthorized

## MODIFIED Requirements

### Requirement: Security adapters under infrastructure/security/
The system SHALL place bcrypt password hashing, JWT token processing, refresh token management (RefreshToken dataclass, RefreshTokenRepository protocol, RefreshTokenService, RefreshTokenIdGenerator, AccessTokenEncoder), and identity provision under `infrastructure/security/`.

#### Scenario: Password hasher implements domain port
- **WHEN** `BcryptPasswordHasher` is defined in `infrastructure/security/`
- **THEN** it implements the `PasswordHasher` protocol defined in the domain or application layer

#### Scenario: RefreshTokenService lives in infrastructure/security/
- **WHEN** inspecting `infrastructure/security/refresh_token_service.py`
- **THEN** it contains the full refresh token lifecycle logic (issue, rotate, revoke)

#### Scenario: All token-related protocols are defined in infrastructure/security/
- **WHEN** searching for `RefreshTokenIdGenerator` and `AccessTokenEncoder` protocol definitions
- **THEN** they are defined in `infrastructure/security/` (not in domain)
