from dishka import Provider, Scope, from_context, provide
from starlette.requests import Request

from features.account.entrypoint.rest.access_token_processor_jwt import (
    JwtAccessTokenProcessor,
)
from features.account.entrypoint.rest.cookie_params import CookieParams
from setup.config.security import SecuritySettings


class PresentationProvider(Provider):
    scope = Scope.REQUEST

    request = from_context(provides=Request)

    @provide
    def provide_access_token_processor(
        self,
        security: SecuritySettings,
    ) -> JwtAccessTokenProcessor:
        return JwtAccessTokenProcessor(
            secret=security.auth.jwt_secret,
            algorithm=security.auth.jwt_algorithm,
        )

    @provide
    def provide_cookie_params(self, security: SecuritySettings) -> CookieParams:
        return CookieParams(secure=security.cookies.secure)
