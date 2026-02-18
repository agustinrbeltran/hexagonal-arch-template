## MODIFIED Requirements

### Requirement: TokenPairIssuer port at account/application/shared/token_pair_issuer.py
The system SHALL define a `TokenPairIssuer` protocol in `account/application/shared/token_pair_issuer.py` with a single method: `issue_token_pair(account_id: AccountId) -> tuple[str, str]` returning `(access_token, refresh_token_id)`. The parameter type SHALL be `AccountId` (from shared kernel) instead of `UserId`.

#### Scenario: TokenPairIssuer is a Protocol
- **WHEN** inspecting `TokenPairIssuer` in `account/application/shared/token_pair_issuer.py`
- **THEN** it is defined as a `typing.Protocol` with an abstract `issue_token_pair` method

#### Scenario: TokenPairIssuer accepts AccountId and returns token pair
- **WHEN** `issue_token_pair(account_id)` is called
- **THEN** it returns a tuple of `(access_token_str, refresh_token_id_str)`

### Requirement: TokenPairRefresher port at account/application/shared/token_pair_refresher.py
The system SHALL define a `TokenPairRefresher` protocol in `account/application/shared/token_pair_refresher.py` with a single method: `refresh(refresh_token_id: str) -> tuple[str, str]` returning `(access_token, new_refresh_token_id)`.

#### Scenario: TokenPairRefresher is a Protocol
- **WHEN** inspecting `TokenPairRefresher` in `account/application/shared/token_pair_refresher.py`
- **THEN** it is defined as a `typing.Protocol` with an abstract `refresh` method

### Requirement: TokenPairIssuer exposes access token expiry
The `TokenPairIssuer` protocol SHALL also expose the access token expiry duration so handlers can include `expires_in` in their response. This MAY be a property `access_token_expiry_seconds: int` on the protocol, or the `issue_token_pair` return type MAY include it.

#### Scenario: Handler can determine access token expiry
- **WHEN** `LogInHandler` or `RefreshTokenHandler` needs to return `expires_in`
- **THEN** it can obtain the value from the port without accessing private attributes
