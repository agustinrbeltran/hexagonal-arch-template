## ADDED Requirements

### Requirement: TokenPairIssuer port at application/shared/token_pair_issuer.py
The system SHALL define a `TokenPairIssuer` protocol in `application/shared/token_pair_issuer.py` with a single method: `issue_token_pair(user_id: UserId) -> tuple[str, str]` returning `(access_token, refresh_token_id)`. This is a driven port used by application handlers that need to issue auth tokens after successful authentication.

#### Scenario: TokenPairIssuer is a Protocol
- **WHEN** inspecting `TokenPairIssuer` in `application/shared/token_pair_issuer.py`
- **THEN** it is defined as a `typing.Protocol` with an abstract `issue_token_pair` method

#### Scenario: TokenPairIssuer accepts UserId and returns token pair
- **WHEN** `issue_token_pair(user_id)` is called
- **THEN** it returns a tuple of `(access_token_str, refresh_token_id_str)`

#### Scenario: LogInHandler depends on TokenPairIssuer port
- **WHEN** inspecting `LogInHandler.__init__`
- **THEN** it accepts a `TokenPairIssuer` dependency, not a concrete `RefreshTokenService`

### Requirement: TokenPairRefresher port at application/shared/token_pair_refresher.py
The system SHALL define a `TokenPairRefresher` protocol in `application/shared/token_pair_refresher.py` with a single method: `refresh(refresh_token_id: str) -> tuple[str, str]` returning `(access_token, new_refresh_token_id)`. This is a driven port used by the refresh-token use case handler.

#### Scenario: TokenPairRefresher is a Protocol
- **WHEN** inspecting `TokenPairRefresher` in `application/shared/token_pair_refresher.py`
- **THEN** it is defined as a `typing.Protocol` with an abstract `refresh` method

#### Scenario: TokenPairRefresher accepts token ID and returns new pair
- **WHEN** `refresh(refresh_token_id)` is called with a valid token
- **THEN** it returns a tuple of `(new_access_token_str, new_refresh_token_id_str)`

#### Scenario: RefreshTokenHandler depends on TokenPairRefresher port
- **WHEN** inspecting `RefreshTokenHandler.__init__`
- **THEN** it accepts a `TokenPairRefresher` dependency, not a concrete `RefreshTokenService`

### Requirement: TokenPairIssuer exposes access token expiry
The `TokenPairIssuer` protocol SHALL also expose the access token expiry duration so handlers can include `expires_in` in their response. This MAY be a property `access_token_expiry_seconds: int` on the protocol, or the `issue_token_pair` return type MAY include it.

#### Scenario: Handler can determine access token expiry
- **WHEN** `LogInHandler` or `RefreshTokenHandler` needs to return `expires_in`
- **THEN** it can obtain the value from the port without accessing private attributes
