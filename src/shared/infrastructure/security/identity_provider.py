import logging
from uuid import UUID

from starlette.requests import Request

from account.infrastructure.security.access_token_processor_jwt import (
    JwtAccessTokenProcessor,
)
from shared.domain.account_id import AccountId
from shared.domain.errors import AuthenticationError
from shared.domain.ports.identity_provider import IdentityProvider

log = logging.getLogger(__name__)

AUTH_NOT_AUTHENTICATED = "Not authenticated."
AUTH_INVALID_TOKEN = "Invalid or expired access token."  # noqa: S105


class JwtBearerIdentityProvider(IdentityProvider):
    def __init__(
        self,
        request: Request,
        access_token_processor: JwtAccessTokenProcessor,
    ) -> None:
        self._request = request
        self._access_token_processor = access_token_processor

    async def get_current_account_id(self) -> AccountId:
        """:raises AuthenticationError:"""
        auth_header: str | None = self._request.headers.get("authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

        token = auth_header[len("Bearer ") :]
        account_id_str = self._access_token_processor.decode_account_id(token)
        if account_id_str is None:
            raise AuthenticationError(AUTH_INVALID_TOKEN)

        return AccountId(UUID(account_id_str))
