import logging
from datetime import datetime
from typing import Any, Literal, TypedDict, cast

import jwt

from domain.refresh_token.services import AccessTokenEncoder
from domain.user.value_objects import UserId

log = logging.getLogger(__name__)

ACCESS_TOKEN_INVALID_OR_EXPIRED = "Invalid or expired JWT."
ACCESS_TOKEN_PAYLOAD_MISSING = "JWT payload missing claim."


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

    def encode(self, user_id: UserId, expiration: datetime) -> str:
        now = datetime.now(tz=expiration.tzinfo)
        payload = JwtPayload(
            sub=str(user_id.value),
            exp=int(expiration.timestamp()),
            iat=int(now.timestamp()),
        )
        return jwt.encode(
            cast(dict[str, Any], payload),
            key=self._secret,
            algorithm=self._algorithm,
        )

    def decode_user_id(self, token: str) -> str | None:
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
