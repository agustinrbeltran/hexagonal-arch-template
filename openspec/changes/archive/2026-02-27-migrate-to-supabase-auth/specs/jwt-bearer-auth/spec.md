## MODIFIED Requirements

### Requirement: Stateless JWT access token with standard claims
The system SHALL verify JWT access tokens issued by the external auth provider (Supabase GoTrue). Tokens contain payload `{sub: str(account_id), exp: int, iat: int, aud: "authenticated", ...}`. The `sub` claim MUST contain the string representation of the account's UUID. The backend SHALL NOT issue its own JWTs — it only verifies tokens using the shared JWT secret.

#### Scenario: Access token contains sub claim as account UUID
- **WHEN** an access token is decoded
- **THEN** its `sub` claim contains the account UUID string

#### Scenario: Access token audience is validated
- **WHEN** an access token is decoded
- **THEN** the `aud` claim MUST equal `"authenticated"`

#### Scenario: Backend does not encode JWTs
- **WHEN** inspecting the access token processor
- **THEN** it only has decode/verify methods, no encode method

### Requirement: Bearer token authentication via Authorization header
The system SHALL authenticate requests by reading the `Authorization: Bearer <token>` header. The identity provider MUST decode the JWT, validate the signature, expiration, and audience, and extract the `account_id` from the `sub` claim. No database lookup SHALL occur during token validation itself.

#### Scenario: Valid Bearer token extracts account ID
- **WHEN** a request includes `Authorization: Bearer <valid-jwt>`
- **THEN** the identity provider returns the `AccountId` from the `sub` claim without a database query

#### Scenario: Expired Bearer token is rejected
- **WHEN** a request includes a Bearer token whose `exp` is in the past
- **THEN** the identity provider raises an authentication error

#### Scenario: Invalid audience is rejected
- **WHEN** a request includes a Bearer token whose `aud` is not `"authenticated"`
- **THEN** the identity provider raises an authentication error
