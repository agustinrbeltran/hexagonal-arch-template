import logging

import jwt

log = logging.getLogger(__name__)

ACCESS_TOKEN_INVALID_OR_EXPIRED = "Invalid or expired JWT."  # noqa: S105
ACCESS_TOKEN_PAYLOAD_MISSING = "JWT payload missing claim."  # noqa: S105


class AccessTokenDecoder:
    def __init__(
        self,
        secret: str,
        algorithm: str,
        jwks_url: str | None = None,
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._jwk_client = jwt.PyJWKClient(jwks_url) if jwks_url else None

    def decode_account_id(self, token: str) -> str | None:
        try:
            if self._jwk_client:
                signing_key = self._jwk_client.get_signing_key_from_jwt(token)
                key = signing_key.key
            else:
                key = self._secret

            payload = jwt.decode(
                token,
                key=key,
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
