import logging
from abc import abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Protocol

from account.application.shared.token_pair_issuer import TokenPairIssuer
from account.application.shared.token_pair_refresher import TokenPairRefresher
from account.infrastructure.security.errors import (
    RefreshTokenExpiredError,
    RefreshTokenNotFoundError,
)
from account.infrastructure.security.refresh_token import RefreshToken
from account.infrastructure.security.refresh_token_repository import (
    RefreshTokenRepository,
)
from shared.domain.account_id import AccountId

log = logging.getLogger(__name__)

TOKEN_NOT_FOUND: str = "Refresh token not found."  # noqa: S105
TOKEN_EXPIRED: str = "Refresh token has expired."  # noqa: S105


class RefreshTokenIdGenerator(Protocol):
    @abstractmethod
    def generate(self) -> str: ...


class AccessTokenEncoder(Protocol):
    @abstractmethod
    def encode(self, account_id: AccountId, expiration: datetime) -> str: ...


class RefreshTokenService(TokenPairIssuer, TokenPairRefresher):
    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepository,
        refresh_token_id_generator: RefreshTokenIdGenerator,
        access_token_encoder: AccessTokenEncoder,
        access_token_expiry_min: int,
        refresh_token_expiry_days: int,
    ) -> None:
        self._repository = refresh_token_repository
        self._id_generator = refresh_token_id_generator
        self._access_token_encoder = access_token_encoder
        self._access_token_expiry_min = access_token_expiry_min
        self._refresh_token_expiry_days = refresh_token_expiry_days

    @property
    def access_token_expiry_seconds(self) -> int:
        return self._access_token_expiry_min * 60

    def issue_token_pair(self, account_id: AccountId) -> tuple[str, str]:
        log.debug("Issue token pair: started. Account ID: '%s'.", account_id.value)

        refresh_token = self._create_refresh_token(account_id)
        self._repository.add(refresh_token)

        access_token = self._create_access_token(account_id)

        log.debug(
            "Issue token pair: done. Account ID: '%s', Refresh token ID: '%s'.",
            account_id.value,
            refresh_token.id_,
        )
        return access_token, refresh_token.id_

    async def refresh(self, refresh_token_id: str) -> tuple[str, str]:
        """:raises RefreshTokenNotFoundError, RefreshTokenExpiredError:"""
        log.debug("Refresh token: started. Refresh token ID: '%s'.", refresh_token_id)

        old_token = await self._repository.get_by_id(refresh_token_id)
        if old_token is None:
            raise RefreshTokenNotFoundError(TOKEN_NOT_FOUND)

        if old_token.expiration <= datetime.now(tz=UTC):
            await self._repository.delete(refresh_token_id)
            raise RefreshTokenExpiredError(TOKEN_EXPIRED)

        await self._repository.delete(refresh_token_id)

        new_refresh_token = self._create_refresh_token(old_token.account_id)
        self._repository.add(new_refresh_token)

        access_token = self._create_access_token(old_token.account_id)

        log.debug(
            "Refresh token: done. Account ID: '%s', New refresh token ID: '%s'.",
            old_token.account_id.value,
            new_refresh_token.id_,
        )
        return access_token, new_refresh_token.id_

    async def revoke_all_for_account(self, account_id: AccountId) -> None:
        """:raises DataMapperError:"""
        log.debug(
            "Revoke all refresh tokens: started. Account ID: '%s'.", account_id.value
        )
        await self._repository.delete_all_for_account(account_id)
        log.debug(
            "Revoke all refresh tokens: done. Account ID: '%s'.", account_id.value
        )

    def _create_refresh_token(self, account_id: AccountId) -> RefreshToken:
        return RefreshToken(
            id_=self._id_generator.generate(),
            account_id=account_id,
            expiration=datetime.now(tz=UTC)
            + timedelta(days=self._refresh_token_expiry_days),
        )

    def _create_access_token(self, account_id: AccountId) -> str:
        expiration = datetime.now(tz=UTC) + timedelta(
            minutes=self._access_token_expiry_min
        )
        return self._access_token_encoder.encode(account_id, expiration)
