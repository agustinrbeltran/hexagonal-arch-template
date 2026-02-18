import logging
from datetime import datetime
from typing import Any, Literal, TypedDict, cast

import jwt

from account.infrastructure.security.refresh_token_service import AccessTokenEncoder
from shared.domain.account_id import AccountId

log = logging.getLogger(__name__)

ACCESS_TOKEN_INVALID_OR_EXPIRED = "Invalid or expired JWT."  # noqa: S105
ACCESS_TOKEN_PAYLOAD_MISSING = "JWT payload missing claim."  # noqa: S105


class JwtPayload(TypedDict):
    sub: str
    exp: int
    iat: int


class JwtAccessTokenProcessor(AccessTokenEncoder):
    def __init__(
        self,
        secret: str,
        algorithm: Literal[
            "HS256",
            "HS384",
            "HS512",
            "RS256",
            "RS384",
            "RS512",
        ],
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm

    def encode(self, account_id: AccountId, expiration: datetime) -> str:
        now = datetime.now(tz=expiration.tzinfo)
        payload = JwtPayload(
            sub=str(account_id.value),
            exp=int(expiration.timestamp()),
            iat=int(now.timestamp()),
        )
        return jwt.encode(
            cast(dict[str, Any], payload),
            key=self._secret,
            algorithm=self._algorithm,
        )

    def decode_account_id(self, token: str) -> str | None:
        try:
            payload = jwt.decode(
                token,
                key=self._secret,
                algorithms=[self._algorithm],
            )
        except jwt.PyJWTError as err:
            log.debug("%s %s", ACCESS_TOKEN_INVALID_OR_EXPIRED, err)
            return None

        sub: str | None = payload.get("sub")
        if sub is None:
            log.debug("%s 'sub'", ACCESS_TOKEN_PAYLOAD_MISSING)
            return None

        return sub
