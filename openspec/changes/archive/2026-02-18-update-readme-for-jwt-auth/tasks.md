## 1. Remove AuthSession Domain Aggregate References

- [x] 1.1 Update domain layer description (~L104-223): Remove AuthSession from "Aggregates in this project" list, remove the AuthSession aggregate boundary diagram, update text to state only User aggregate exists
- [x] 1.2 Update DDD Patterns - Aggregates section (~L418-492): Remove AuthSession from aggregate listing, update aggregate count references
- [x] 1.3 Update Domain Events section (~L494-557): Remove session-related event examples (SessionCreated, SessionTerminated), keep only User events

## 2. Update Authentication Documentation

- [x] 2.1 Update Application Layer examples (~L226-319): Rewrite LogInHandler example to show token pair issuance (TokenPairIssuer) instead of AuthSession creation
- [x] 2.2 Update Infrastructure Layer examples (~L323-405): Replace SqlaAuthSessionGateway example with JWT/refresh token infrastructure references
- [x] 2.3 Update Domain Services section (~L700-797): Remove AuthSessionService example, replace with current domain service examples
- [x] 2.4 Update Application Services section (~L798-867): Update CreateUserHandler or LogInHandler example to match current code

## 3. Update Request Flow

- [x] 3.1 Rewrite Request Flow Example section (~L1106-1370): Replace session-based flow with JWT token-based flow showing access token issuance and refresh token storage

## 4. Update Project Structure

- [x] 4.1 Update the project structure tree (~L1576-1693): Add new files (application/refresh_token/, infrastructure/security/ JWT files, token_pair_issuer, token_pair_refresher), remove domain/auth_session/, update persistence section

## 5. Update API Endpoints

- [x] 5.1 Update Account endpoints section (~L1796-1817): Remove `/logout` endpoint, add `/refresh` endpoint, update login/signup descriptions to mention JWT tokens instead of cookies
- [x] 5.2 Update the footnote (~L2081-2083): Update or remove the session/token footnote to reflect current JWT architecture

## 6. Update Configuration

- [x] 6.1 Update Configuration section: Add JWT-related settings (JWT_ALGORITHM, ACCESS_TOKEN_EXPIRY_MIN, REFRESH_TOKEN_EXPIRY_DAYS) and mention JWT_SECRET in secrets documentation

## 7. Minor Cleanup

- [x] 7.1 Update Hexagonal Architecture Continued section (~L1028-1100): Fix file path references from old feature-based paths to current layer-based paths
- [x] 7.2 Update Note on Adapters section (~L985-1016): Fix file path examples from old feature-based paths to current layer-based paths
- [x] 7.3 Review and update the Todo section at the bottom of the README
