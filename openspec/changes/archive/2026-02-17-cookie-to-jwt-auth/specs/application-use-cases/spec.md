## REMOVED Requirements

### Requirement: Application use cases cover all existing operations
**Reason**: The `log_out` use case is removed because stateless JWT tokens are discarded client-side — there is no server-side session to terminate. The requirement is being replaced with an updated list that excludes `log_out` and adds `refresh_token`.
**Migration**: Delete `src/application/log_out/` directory entirely. Remove logout route from account router.

## ADDED Requirements

### Requirement: Application use cases cover all operations
The system SHALL provide use case directories for all operations: `create_user`, `activate_user`, `deactivate_user`, `grant_admin`, `revoke_admin`, `set_user_password`, `list_users`, `current_user`, `sign_up`, `log_in`, `change_password`, `refresh_token`.

#### Scenario: All endpoints have corresponding use cases
- **WHEN** listing directories under `src/application/`
- **THEN** there is one directory per REST endpoint operation, including `refresh_token` and excluding `log_out`

### Requirement: LogInHandler returns a token pair
The `LogInHandler` MUST return a token pair (access token string + refresh token string) instead of returning `None`. It SHALL call `RefreshTokenService.issue_token_pair(user_id)` after credential validation. The handler MUST NOT check for "already authenticated" status — any valid credentials produce a new token pair.

#### Scenario: Login issues token pair
- **WHEN** `LogInHandler.execute(command)` succeeds
- **THEN** it returns an `(access_token, refresh_token)` tuple from `RefreshTokenService.issue_token_pair()`

#### Scenario: Login does not check existing authentication
- **WHEN** `LogInHandler.execute(command)` is called
- **THEN** it does NOT call `CurrentUserHandler` or check for existing sessions

### Requirement: RefreshTokenHandler use case at application/refresh_token/
The system SHALL provide a `refresh_token` use case with `command.py` (containing `RefreshTokenCommand` with a `refresh_token: str` field), `handler.py` (containing `RefreshTokenHandler`), and `port.py` (containing `RefreshTokenUseCase` ABC). The handler MUST call `RefreshTokenService.refresh(token_id)` and return a new token pair.

#### Scenario: RefreshTokenHandler returns new token pair
- **WHEN** `RefreshTokenHandler.execute(command)` is called with a valid refresh token
- **THEN** it returns a new `(access_token, refresh_token)` tuple

#### Scenario: RefreshTokenHandler propagates domain errors
- **WHEN** `RefreshTokenHandler.execute(command)` is called with an invalid refresh token
- **THEN** it propagates `RefreshTokenNotFoundError` or `RefreshTokenExpiredError`
