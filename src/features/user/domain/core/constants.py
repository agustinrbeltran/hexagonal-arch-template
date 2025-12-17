from typing import Final

AUTHZ_NOT_AUTHORIZED: Final[str] = "Not authorized."
AUTHZ_NO_CURRENT_USER: Final[str] = (
    "Failed to retrieve current user. Removing all access."
)
AUTH_ACCOUNT_INACTIVE: Final[str] = "Your account is inactive. Please contact support."
AUTH_ALREADY_AUTHENTICATED: Final[str] = (
    "You are already authenticated. Consider logging out."
)
AUTH_PASSWORD_INVALID: Final[str] = "Invalid password."
AUTH_PASSWORD_NEW_SAME_AS_CURRENT: Final[str] = (
    "New password must differ from current password."
)
