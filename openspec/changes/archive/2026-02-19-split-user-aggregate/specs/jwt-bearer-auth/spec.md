## MODIFIED Requirements

### Requirement: Stateless JWT access token with standard claims
The system SHALL issue JWT access tokens with payload `{sub: str(account_id), exp: int, iat: int}` using RFC 7519 standard claims. The `sub` claim MUST contain the string representation of the account's UUID. The token MUST be signed using the configured algorithm and secret.

#### Scenario: Access token contains only standard claims
- **WHEN** an access token is decoded
- **THEN** its payload contains exactly `sub`, `exp`, and `iat` claims

#### Scenario: Sub claim is the account UUID string
- **WHEN** an access token is issued for an account with ID `550e8400-e29b-41d4-a716-446655440000`
- **THEN** the `sub` claim equals `"550e8400-e29b-41d4-a716-446655440000"`

### Requirement: Bearer token authentication via Authorization header
The system SHALL authenticate requests by reading the `Authorization: Bearer <token>` header. The identity provider MUST decode the JWT, validate the signature and expiration, and extract the `account_id` from the `sub` claim. No database lookup SHALL occur during token validation itself.

#### Scenario: Valid Bearer token extracts account ID
- **WHEN** a request includes `Authorization: Bearer <valid-jwt>`
- **THEN** the identity provider returns the `AccountId` from the `sub` claim without a database query

#### Scenario: Expired Bearer token is rejected
- **WHEN** a request includes a Bearer token whose `exp` is in the past
- **THEN** the identity provider raises an authentication error

### Requirement: is_active check on every authenticated request
The system SHALL verify that the authenticated account's `is_active` flag is `true` on every authenticated request via `CurrentAccountHandler`. If the account is inactive, the request MUST be rejected with an authorization error and all refresh tokens for that account MUST be revoked.

#### Scenario: Inactive account is rejected despite valid token
- **WHEN** an account with a valid access token makes a request but the account has been deactivated
- **THEN** `CurrentAccountHandler` raises an `AuthorizationError` and calls `AccessRevoker.remove_all_account_access()`
