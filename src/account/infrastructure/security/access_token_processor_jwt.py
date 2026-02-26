import logging
from typing import Literal

import jwt

log = logging.getLogger(__name__)

ACCESS_TOKEN_INVALID_OR_EXPIRED = "Invalid or expired JWT."  # noqa: S105
ACCESS_TOKEN_PAYLOAD_MISSING = "JWT payload missing claim."  # noqa: S105


class AccessTokenDecoder:
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

    def decode_account_id(self, token: str) -> str | None:
        try:
            payload = jwt.decode(
                token,
                key=self._secret,
                algorithms=[self._algorithm],
                audience="authenticated",
            )
        except jwt.PyJWTError as err:
            log.debug("%s %s", ACCESS_TOKEN_INVALID_OR_EXPIRED, err)
            return None

        sub: str | None = payload.get("sub")
        if sub is None:
            log.debug("%s 'sub'", ACCESS_TOKEN_PAYLOAD_MISSING)
            return None

        return sub
