import logging
from abc import abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Protocol

from domain.refresh_token.entity import RefreshToken
from domain.refresh_token.errors import RefreshTokenExpiredError, RefreshTokenNotFoundError
from domain.refresh_token.repository import RefreshTokenRepository
from domain.user.value_objects import UserId

log = logging.getLogger(__name__)

TOKEN_NOT_FOUND: str = "Refresh token not found."
TOKEN_EXPIRED: str = "Refresh token has expired."


class RefreshTokenIdGenerator(Protocol):
    @abstractmethod
    def generate(self) -> str: ...


class AccessTokenEncoder(Protocol):
    @abstractmethod
    def encode(self, user_id: UserId, expiration: datetime) -> str: ...


class RefreshTokenService:
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

    def issue_token_pair(self, user_id: UserId) -> tuple[str, str]:
        log.debug("Issue token pair: started. User ID: '%s'.", user_id.value)

        refresh_token = self._create_refresh_token(user_id)
        self._repository.add(refresh_token)

        access_token = self._create_access_token(user_id)

        log.debug(
            "Issue token pair: done. User ID: '%s', Refresh token ID: '%s'.",
            user_id.value,
            refresh_token.id_,
        )
        return access_token, refresh_token.id_

    async def refresh(self, refresh_token_id: str) -> tuple[str, str]:
        """:raises RefreshTokenNotFoundError, RefreshTokenExpiredError:"""
        log.debug(
            "Refresh token: started. Refresh token ID: '%s'.", refresh_token_id
        )

        old_token = await self._repository.get_by_id(refresh_token_id)
        if old_token is None:
            raise RefreshTokenNotFoundError(TOKEN_NOT_FOUND)

        if old_token.expiration <= datetime.now(tz=UTC):
            await self._repository.delete(refresh_token_id)
            raise RefreshTokenExpiredError(TOKEN_EXPIRED)

        await self._repository.delete(refresh_token_id)

        new_refresh_token = self._create_refresh_token(old_token.user_id)
        self._repository.add(new_refresh_token)

        access_token = self._create_access_token(old_token.user_id)

        log.debug(
            "Refresh token: done. User ID: '%s', New refresh token ID: '%s'.",
            old_token.user_id.value,
            new_refresh_token.id_,
        )
        return access_token, new_refresh_token.id_

    async def revoke_all_for_user(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""
        log.debug(
            "Revoke all refresh tokens: started. User ID: '%s'.", user_id.value
        )
        await self._repository.delete_all_for_user(user_id)
        log.debug(
            "Revoke all refresh tokens: done. User ID: '%s'.", user_id.value
        )

    def _create_refresh_token(self, user_id: UserId) -> RefreshToken:
        return RefreshToken(
            id_=self._id_generator.generate(),
            user_id=user_id,
            expiration=datetime.now(tz=UTC)
            + timedelta(days=self._refresh_token_expiry_days),
        )

    def _create_access_token(self, user_id: UserId) -> str:
        expiration = datetime.now(tz=UTC) + timedelta(
            minutes=self._access_token_expiry_min
        )
        return self._access_token_encoder.encode(user_id, expiration)
