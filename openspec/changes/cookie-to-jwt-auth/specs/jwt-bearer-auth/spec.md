## ADDED Requirements

### Requirement: Stateless JWT access token with standard claims
The system SHALL issue JWT access tokens with payload `{sub: str(user_id), exp: int, iat: int}` using RFC 7519 standard claims. The `sub` claim MUST contain the string representation of the user's UUID. The token MUST be signed using the configured algorithm and secret. Access tokens MUST NOT contain any other claims (no role, no session ID).

#### Scenario: Access token contains only standard claims
- **WHEN** an access token is decoded
- **THEN** its payload contains exactly `sub`, `exp`, and `iat` claims

#### Scenario: Sub claim is the user UUID string
- **WHEN** an access token is issued for a user with ID `550e8400-e29b-41d4-a716-446655440000`
- **THEN** the `sub` claim equals `"550e8400-e29b-41d4-a716-446655440000"`

#### Scenario: Access token expiry matches configuration
- **WHEN** an access token is issued with `ACCESS_TOKEN_EXPIRY_MIN = 15`
- **THEN** the `exp` claim is 900 seconds after `iat`

### Requirement: Bearer token authentication via Authorization header
The system SHALL authenticate requests by reading the `Authorization: Bearer <token>` header. The identity provider MUST decode the JWT, validate the signature and expiration, and extract the `user_id` from the `sub` claim. No database lookup SHALL occur during token validation itself.

#### Scenario: Valid Bearer token extracts user ID
- **WHEN** a request includes `Authorization: Bearer <valid-jwt>`
- **THEN** the identity provider returns the `user_id` from the `sub` claim without a database query

#### Scenario: Expired Bearer token is rejected
- **WHEN** a request includes a Bearer token whose `exp` is in the past
- **THEN** the identity provider raises an authentication error

#### Scenario: Invalid Bearer token is rejected
- **WHEN** a request includes a Bearer token with an invalid signature
- **THEN** the identity provider raises an authentication error

#### Scenario: Missing Authorization header is rejected
- **WHEN** a request has no `Authorization` header
- **THEN** the identity provider raises an authentication error

### Requirement: Login returns token pair in JSON response body
The system SHALL return access and refresh tokens as a JSON response from the login endpoint with HTTP status 200. The response body MUST contain: `access_token` (string), `refresh_token` (string), `token_type` (literal "bearer"), `expires_in` (int, seconds until access token expiry).

#### Scenario: Successful login returns token pair
- **WHEN** a user logs in with valid credentials
- **THEN** the response is `200 OK` with JSON body containing `access_token`, `refresh_token`, `token_type`, and `expires_in`

#### Scenario: Token type is bearer
- **WHEN** a successful login response is returned
- **THEN** `token_type` equals `"bearer"`

#### Scenario: Expires_in matches access token lifetime
- **WHEN** a successful login response is returned with `ACCESS_TOKEN_EXPIRY_MIN = 15`
- **THEN** `expires_in` equals `900`

### Requirement: OpenAPI security scheme is HTTPBearer
The system SHALL declare the OpenAPI security scheme as `HTTPBearer`. All authenticated endpoints MUST reference this scheme for Swagger UI to display the "Authorize" button accepting a Bearer token.

#### Scenario: Swagger UI shows Bearer auth
- **WHEN** the OpenAPI schema is inspected
- **THEN** the security scheme type is `http` with scheme `bearer` and bearerFormat `JWT`

### Requirement: No cookies or cookie middleware
The system SHALL NOT set, read, or manage HTTP cookies for authentication. The ASGI cookie middleware MUST be removed. No `Set-Cookie` headers SHALL be sent for authentication purposes.

#### Scenario: Login does not set cookies
- **WHEN** a successful login response is returned
- **THEN** no `Set-Cookie` header is present in the response

### Requirement: is_active check on every authenticated request
The system SHALL verify that the authenticated user's `is_active` flag is `true` on every authenticated request via `CurrentUserHandler`. If the user is inactive, the request MUST be rejected with an authorization error and all refresh tokens for that user MUST be revoked.

#### Scenario: Inactive user is rejected despite valid token
- **WHEN** a user with a valid access token makes a request but their account has been deactivated
- **THEN** `CurrentUserHandler` raises an `AuthorizationError` and calls `AccessRevoker.remove_all_user_access()`
