## ADDED Requirements

### Requirement: Integration test infrastructure with Dishka provider overrides
The system SHALL provide a test app factory that creates a real FastAPI application with real Dishka DI wiring, but with mocked external boundaries (repositories, Supabase auth adapters, identity provider). The test app SHALL use a test-specific lifespan that performs table mapping and event handler discovery but skips the outbox relay.

#### Scenario: Test app boots with override providers
- **WHEN** the test app factory is invoked with mock providers and programmatic test settings
- **THEN** a FastAPI application is created with all routes registered, Dishka container wired, and mock implementations bound for all repository and Supabase auth Protocols

#### Scenario: Test lifespan maps tables without relay
- **WHEN** the test app starts its lifespan
- **THEN** SQLAlchemy imperative table mappings are applied and event handlers are discovered, but no OutboxRelay background task is started

### Requirement: FakeIdentityProvider for auth control
The system SHALL provide a `FakeIdentityProvider` implementing `IdentityProvider` that returns a configurable `AccountId`. Tests SHALL control the authenticated identity by calling `set_current_account(account_id)`.

#### Scenario: Protected endpoint with configured identity
- **WHEN** a test sets `fake_identity.set_current_account(some_id)` and sends a request with `Authorization: Bearer test-token`
- **THEN** the identity provider returns `some_id` as the current account ID

#### Scenario: Protected endpoint without configured identity
- **WHEN** a test does not configure the fake identity and sends a request with a Bearer token
- **THEN** the identity provider raises `AuthenticationError`

### Requirement: httpx AsyncClient fixture
The system SHALL provide a pytest fixture that creates an `httpx.AsyncClient` with `ASGITransport` bound to the test app, enabling async HTTP requests without a running server.

#### Scenario: Client sends request to test app
- **WHEN** a test uses the async client to send a request
- **THEN** the request is routed through the real FastAPI app and returns a response

### Requirement: Health endpoint returns 200
The `GET /api/v1/health` endpoint SHALL return status 200 with body `{"status": "ok"}`.

#### Scenario: Health check succeeds
- **WHEN** a GET request is sent to `/api/v1/health`
- **THEN** the response status is 200 and body is `{"status": "ok"}`

### Requirement: Root endpoint redirects to docs
The `GET /` endpoint SHALL redirect to `/docs/`.

#### Scenario: Root redirects
- **WHEN** a GET request is sent to `/` without following redirects
- **THEN** the response status is 307 with `Location` header pointing to `/docs/`

### Requirement: Signup endpoint validates and creates account
The `POST /api/v1/accounts/signup` endpoint SHALL accept email and password, invoke the sign-up use case, and return 201 with the new account ID.

#### Scenario: Successful signup
- **WHEN** a POST request is sent with valid email and password
- **THEN** the response status is 201 and body contains the account `id`

#### Scenario: Signup with duplicate email
- **WHEN** the sign-up use case raises `EmailAlreadyExistsError`
- **THEN** the response status is 409

#### Scenario: Signup with invalid email format
- **WHEN** a POST request is sent with an invalid email
- **THEN** the response status is 400

### Requirement: Login endpoint authenticates and returns tokens
The `POST /api/v1/accounts/login` endpoint SHALL accept email and password, invoke the login use case, and return 200 with access and refresh tokens.

#### Scenario: Successful login
- **WHEN** a POST request is sent with valid credentials
- **THEN** the response status is 200 and body contains `access_token`, `refresh_token`, `token_type`, and `expires_in`

#### Scenario: Login with invalid credentials
- **WHEN** the login use case raises `AuthenticationError`
- **THEN** the response status is 401

### Requirement: Refresh endpoint issues new token pair
The `POST /api/v1/accounts/refresh` endpoint SHALL accept a refresh token and return a new token pair.

#### Scenario: Successful refresh
- **WHEN** a POST request is sent with a valid refresh token
- **THEN** the response status is 200 and body contains new `access_token` and `refresh_token`

### Requirement: Current account endpoint returns authenticated account
The `GET /api/v1/accounts/me` endpoint SHALL return the current account's details.

#### Scenario: Authenticated request
- **WHEN** an authenticated GET request is sent
- **THEN** the response status is 200 and body contains `id`, `email`, `role`, `is_active`

#### Scenario: Unauthenticated request
- **WHEN** a GET request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Change password endpoint updates own password
The `PUT /api/v1/accounts/password` endpoint SHALL accept current and new passwords for the authenticated user.

#### Scenario: Successful password change
- **WHEN** an authenticated PUT request is sent with valid current and new passwords
- **THEN** the response status is 204

#### Scenario: Unauthenticated request
- **WHEN** a PUT request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Create account endpoint (admin)
The `POST /api/v1/accounts/` endpoint SHALL allow admins to create accounts.

#### Scenario: Admin creates account
- **WHEN** an admin-authenticated POST request is sent with email, password, and role
- **THEN** the response status is 201 and body contains the account `id`

#### Scenario: Unauthenticated request
- **WHEN** a POST request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: List accounts endpoint with pagination
The `GET /api/v1/accounts/` endpoint SHALL return paginated account lists.

#### Scenario: List with defaults
- **WHEN** an authenticated GET request is sent without query params
- **THEN** the response status is 200 and body contains `accounts` array and `total` count

#### Scenario: List with custom pagination
- **WHEN** an authenticated GET request is sent with `limit=5&offset=10`
- **THEN** the pagination params are forwarded to the use case

#### Scenario: Unauthenticated request
- **WHEN** a GET request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Set account password endpoint (admin)
The `PUT /api/v1/accounts/{account_id}/password` endpoint SHALL allow setting another account's password.

#### Scenario: Successful password set
- **WHEN** an authenticated PUT request is sent with a valid password
- **THEN** the response status is 204

#### Scenario: Unauthenticated request
- **WHEN** a PUT request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Grant admin role endpoint
The `PUT /api/v1/accounts/{account_id}/roles/admin` endpoint SHALL grant admin role.

#### Scenario: Successful grant
- **WHEN** an authenticated PUT request is sent for a valid account ID
- **THEN** the response status is 204

#### Scenario: Unauthenticated request
- **WHEN** a PUT request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Revoke admin role endpoint
The `DELETE /api/v1/accounts/{account_id}/roles/admin` endpoint SHALL revoke admin role.

#### Scenario: Successful revoke
- **WHEN** an authenticated DELETE request is sent for a valid account ID
- **THEN** the response status is 204

#### Scenario: Unauthenticated request
- **WHEN** a DELETE request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Activate account endpoint
The `PUT /api/v1/accounts/{account_id}/activation` endpoint SHALL activate an account.

#### Scenario: Successful activation
- **WHEN** an authenticated PUT request is sent for a valid account ID
- **THEN** the response status is 204

#### Scenario: Unauthenticated request
- **WHEN** a PUT request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Deactivate account endpoint
The `DELETE /api/v1/accounts/{account_id}/activation` endpoint SHALL deactivate an account.

#### Scenario: Successful deactivation
- **WHEN** an authenticated DELETE request is sent for a valid account ID
- **THEN** the response status is 204

#### Scenario: Unauthenticated request
- **WHEN** a DELETE request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Get my profile endpoint
The `GET /api/v1/profiles/me` endpoint SHALL return the current user's profile.

#### Scenario: Profile exists
- **WHEN** an authenticated GET request is sent and the profile exists
- **THEN** the response status is 200 and body contains `id`, `account_id`, `username`, `first_name`, `last_name`, `birth_date`

#### Scenario: Unauthenticated request
- **WHEN** a GET request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Update profile endpoint (full replacement)
The `PUT /api/v1/profiles/me` endpoint SHALL replace the current user's profile.

#### Scenario: Successful update
- **WHEN** an authenticated PUT request is sent with profile fields
- **THEN** the response status is 204

#### Scenario: Unauthenticated request
- **WHEN** a PUT request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: Patch profile endpoint (partial update)
The `PATCH /api/v1/profiles/me` endpoint SHALL partially update the current user's profile.

#### Scenario: Successful patch
- **WHEN** an authenticated PATCH request is sent with a subset of profile fields
- **THEN** the response status is 204

#### Scenario: Unauthenticated request
- **WHEN** a PATCH request is sent without Authorization header
- **THEN** the response status is 403

### Requirement: List profiles endpoint with pagination
The `GET /api/v1/profiles/` endpoint SHALL return paginated profile lists.

#### Scenario: List with defaults
- **WHEN** an authenticated GET request is sent without query params
- **THEN** the response status is 200 and body contains `profiles` array and `total` count

#### Scenario: Unauthenticated request
- **WHEN** a GET request is sent without Authorization header
- **THEN** the response status is 403
