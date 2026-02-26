## MODIFIED Requirements

### Requirement: TokenPairIssuer port at account/application/shared/token_pair_issuer.py
The system SHALL define a `TokenPairIssuer` protocol in `account/application/shared/token_pair_issuer.py` with an async method: `issue_token_pair(email: Email, password: RawPassword) -> tuple[str, str]` returning `(access_token, refresh_token)`. The method SHALL authenticate the credentials and issue tokens in a single operation. The port SHALL also expose `access_token_expiry_seconds: int` as a property.

#### Scenario: TokenPairIssuer is a Protocol
- **WHEN** inspecting `TokenPairIssuer` in `account/application/shared/token_pair_issuer.py`
- **THEN** it is defined as a `typing.Protocol` with an abstract `issue_token_pair` method

#### Scenario: TokenPairIssuer accepts email and password
- **WHEN** `issue_token_pair(email, password)` is called with valid credentials
- **THEN** it returns a tuple of `(access_token_str, refresh_token_str)`

#### Scenario: TokenPairIssuer raises on invalid credentials
- **WHEN** `issue_token_pair(email, password)` is called with invalid credentials
- **THEN** an `AuthenticationError` is raised

#### Scenario: Handler can determine access token expiry
- **WHEN** `LogInHandler` needs to return `expires_in`
- **THEN** it can obtain the value from `token_pair_issuer.access_token_expiry_seconds`

### Requirement: TokenPairRefresher port at account/application/shared/token_pair_refresher.py
The system SHALL define a `TokenPairRefresher` protocol in `account/application/shared/token_pair_refresher.py` with an async method: `refresh(refresh_token: str) -> tuple[str, str]` returning `(access_token, new_refresh_token)`.

#### Scenario: TokenPairRefresher is a Protocol
- **WHEN** inspecting `TokenPairRefresher` in `account/application/shared/token_pair_refresher.py`
- **THEN** it is defined as a `typing.Protocol` with an abstract `refresh` method

### Requirement: LogInHandler uses TokenPairIssuer without password verification
The `LogInHandler` SHALL fetch the account by email to check `is_active`, then delegate authentication and token issuance to `TokenPairIssuer.issue_token_pair(email, password)`. The handler SHALL NOT verify passwords itself and SHALL NOT depend on `AccountService`. The handler SHALL NOT depend on `AuthUnitOfWork`.

#### Scenario: Login checks is_active before issuing tokens
- **WHEN** `LogInHandler.execute(LogInCommand)` is called for an active account
- **THEN** it fetches the account by email, verifies `is_active`, calls `token_pair_issuer.issue_token_pair(email, password)`, and returns the tokens

#### Scenario: Login rejects inactive account before auth
- **WHEN** `LogInHandler.execute(LogInCommand)` is called for an inactive account
- **THEN** `AuthenticationError` is raised before `issue_token_pair` is called

## REMOVED Requirements

### Requirement: TokenPairIssuer exposes access token expiry
**Reason**: Merged into the modified `TokenPairIssuer` requirement above. The property is retained but the requirement is consolidated.
**Migration**: No action needed — the property remains on the protocol.
