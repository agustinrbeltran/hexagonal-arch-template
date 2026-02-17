import logging
from uuid import UUID

from starlette.requests import Request

from domain.shared.errors import AuthenticationError
from domain.user.ports import IdentityProvider
from domain.user.value_objects import UserId
from infrastructure.security.access_token_processor_jwt import JwtAccessTokenProcessor

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

    async def get_current_user_id(self) -> UserId:
        """:raises AuthenticationError:"""
        auth_header: str | None = self._request.headers.get("authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

        token = auth_header[len("Bearer ") :]
        user_id_str = self._access_token_processor.decode_user_id(token)
        if user_id_str is None:
            raise AuthenticationError(AUTH_INVALID_TOKEN)

        return UserId(UUID(user_id_str))
