## ADDED Requirements

### Requirement: README reflects current JWT authentication architecture
The README.md SHALL accurately describe the current JWT access token + refresh token authentication system, removing all references to the removed AuthSession domain aggregate and cookie-based sessions.

#### Scenario: AuthSession references removed
- **WHEN** a reader reviews the README domain layer documentation
- **THEN** there SHALL be no references to AuthSession as a domain aggregate, auth session events, or session-based authentication

#### Scenario: JWT authentication documented
- **WHEN** a reader reviews the README authentication documentation
- **THEN** the README SHALL describe JWT access tokens (short-lived, stateless) and refresh tokens (long-lived, server-side stored) as the authentication mechanism

#### Scenario: API endpoints accurate
- **WHEN** a reader reviews the README API section
- **THEN** the documented endpoints SHALL match the current API: no `/logout` endpoint, includes `/refresh` endpoint

#### Scenario: Project structure tree accurate
- **WHEN** a reader reviews the README project structure
- **THEN** the file tree SHALL reflect the current layout including `application/refresh_token/`, infrastructure security files, and absence of `domain/auth_session/`

#### Scenario: Code examples match implementation
- **WHEN** a reader reviews inline code examples
- **THEN** the examples SHALL reflect the current token-based authentication flow rather than session-based flows

#### Scenario: Configuration section includes JWT settings
- **WHEN** a reader reviews the configuration section
- **THEN** the README SHALL mention JWT-related configuration (`JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRY_MIN`, `REFRESH_TOKEN_EXPIRY_DAYS`, `JWT_SECRET`)
