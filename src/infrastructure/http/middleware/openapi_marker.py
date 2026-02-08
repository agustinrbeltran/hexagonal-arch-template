from fastapi.security import APIKeyCookie

from infrastructure.http.middleware.constants import COOKIE_ACCESS_TOKEN_NAME

cookie_scheme = APIKeyCookie(name=COOKIE_ACCESS_TOKEN_NAME)
