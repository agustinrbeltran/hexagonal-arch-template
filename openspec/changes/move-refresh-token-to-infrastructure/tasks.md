## 1. Application-Layer Ports

- [ ] 1.1 Create `TokenPairIssuer` protocol in `application/shared/token_pair_issuer.py` with `issue_token_pair(user_id: UserId) -> tuple[str, str]` and `access_token_expiry_seconds: int` property
- [ ] 1.2 Create `TokenPairRefresher` protocol in `application/shared/token_pair_refresher.py` with `refresh(refresh_token_id: str) -> tuple[str, str]` and `access_token_expiry_seconds: int` property

## 2. Relocate Refresh Token Modules to Infrastructure

- [ ] 2.1 Create `infrastructure/security/refresh_token.py` with the `RefreshToken` dataclass (moved from `domain/refresh_token/entity.py`)
- [ ] 2.2 Create `infrastructure/security/refresh_token_repository.py` with the `RefreshTokenRepository` protocol (moved from `domain/refresh_token/repository.py`)
- [ ] 2.3 Move `RefreshTokenNotFoundError` and `RefreshTokenExpiredError` to `infrastructure/security/errors.py` — change base class from `DomainError` to plain `Exception` (or a new `SecurityError` base)
- [ ] 2.4 Create `infrastructure/security/refresh_token_service.py` with `RefreshTokenService` (moved from `domain/refresh_token/services.py`), implementing both `TokenPairIssuer` and `TokenPairRefresher` ports. Move `RefreshTokenIdGenerator` and `AccessTokenEncoder` protocols into this module.

## 3. Update Application Handlers

- [ ] 3.1 Update `application/log_in/handler.py` — replace `RefreshTokenService` dependency with `TokenPairIssuer` port, remove `expires_in` access via private attribute
- [ ] 3.2 Update `application/refresh_token/handler.py` — replace `RefreshTokenService` dependency with `TokenPairRefresher` port, remove `expires_in` access via private attribute

## 4. Update Infrastructure Consumers

- [ ] 4.1 Update `infrastructure/security/refresh_token_id_generator.py` — change import from `domain.refresh_token.services` to `infrastructure.security.refresh_token_service`
- [ ] 4.2 Update `infrastructure/security/access_revoker.py` — change import from `domain.refresh_token.services` to `infrastructure.security.refresh_token_service`
- [ ] 4.3 Update `infrastructure/security/access_token_processor_jwt.py` — verify and update imports if it implements `AccessTokenEncoder`
- [ ] 4.4 Update `infrastructure/persistence/sqla_refresh_token_repository.py` — change imports from `domain.refresh_token.entity` and `domain.refresh_token.repository` to `infrastructure.security.refresh_token` and `infrastructure.security.refresh_token_repository`
- [ ] 4.5 Update `infrastructure/persistence/mappers/refresh_token.py` — change import from `domain.refresh_token.entity` to `infrastructure.security.refresh_token`

## 5. Update DI Providers

- [ ] 5.1 Update `infrastructure/config/di/application.py` — register `TokenPairIssuer` and `TokenPairRefresher` ports
- [ ] 5.2 Update `infrastructure/config/di/infrastructure.py` — wire `RefreshTokenService` as implementation of both ports, update all import paths from `domain.refresh_token` to `infrastructure.security`
- [ ] 5.3 Remove any `domain.refresh_token` references from `infrastructure/config/di/domain.py` if present

## 6. Update HTTP Error Handling

- [ ] 6.1 Update HTTP error handlers/middleware to map `RefreshTokenNotFoundError` and `RefreshTokenExpiredError` from their new import path in `infrastructure/security/errors.py`

## 7. Delete Domain Refresh Token Package

- [ ] 7.1 Delete `src/domain/refresh_token/` directory entirely (entity.py, repository.py, services.py, errors.py, __init__.py)

## 8. Update Tests

- [ ] 8.1 Update unit test imports — replace all `domain.refresh_token.*` imports with new `infrastructure.security.*` and `application.shared.*` paths
- [ ] 8.2 Update test factories/mocks that reference `RefreshTokenService`, `RefreshToken`, or `RefreshTokenRepository` to use new import paths
- [ ] 8.3 Run full test suite and verify all tests pass: `PYTHONPATH=src python -m pytest tests/ -x -q`
